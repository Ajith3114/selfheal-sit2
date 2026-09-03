<?php
// ============================================================
//  6F School of IT - Scenario 5
//  "Where does the data on this page come from?"
//
//  Two screens, one file:
//    1. a login form  (username + password, checked against the DB)
//    2. after login, the rows of every table in the database
//
//  Both screens get everything from MySQL. Nothing is hardcoded.
//
//  EDIT THE FOUR LINES BELOW, then save. Nothing else.
//  Put this file at:  /var/www/html/index.php
// ============================================================

session_start();                                // remembers who is logged in

$DB_HOST = "YOUR-ENDPOINT.rds.amazonaws.com";   // from step 4 of steps.txt
$DB_USER = "admin";
$DB_PASS = "YOUR-PASSWORD";
$DB_NAME = "workshop";

// ------------------------------------------------------------
// Small helpers. h() is used on EVERY value that came out of the
// database - whatever is stored there is text, not HTML.
// ------------------------------------------------------------
function h($s) { return htmlspecialchars((string)$s, ENT_QUOTES, "UTF-8"); }

function page_head($title) {
    header("Content-Type: text/html; charset=utf-8");
    echo "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>";
    echo "<meta name='viewport' content='width=device-width,initial-scale=1'>";
    echo "<title>" . h($title) . "</title>";
    echo "<style>
      body{font:16px/1.6 system-ui,-apple-system,'Segoe UI',sans-serif;
           max-width:760px;margin:0 auto;padding:40px 20px;color:#1a1d21;background:#f6f7f9}
      .card{background:#fff;border:1px solid #e3e6ea;border-radius:12px;padding:24px;margin-bottom:16px}
      h1{margin:0 0 4px;font-size:24px}
      h2{margin:0 0 12px;font-size:18px}
      .muted{color:#5c6570;font-size:14px;margin:0}
      .up{color:#1a7f4b;font-weight:600}
      .down{color:#b52f4a;font-weight:600}
      code{background:#f6f7f9;border:1px solid #e3e6ea;border-radius:4px;padding:2px 6px;font-size:14px}
      label{display:block;margin:14px 0 4px;font-size:14px;font-weight:600}
      input[type=text],input[type=password]{width:100%;box-sizing:border-box;padding:10px 12px;
           border:1px solid #c9cfd6;border-radius:8px;font-size:16px;background:#fff}
      button{margin-top:18px;width:100%;padding:11px 16px;border:0;border-radius:8px;
           background:#1a1d21;color:#fff;font-size:16px;font-weight:600;cursor:pointer}
      .err{background:#fdeef1;border:1px solid #f3c6cf;color:#b52f4a;
           border-radius:8px;padding:10px 12px;margin-top:14px;font-size:14px}
      .bar{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:4px}
      .bar a{color:#5c6570;font-size:14px}
      .scroll{overflow-x:auto}
      table{border-collapse:collapse;width:100%;font-size:14px}
      th,td{border:1px solid #e3e6ea;padding:8px 10px;text-align:left;vertical-align:top}
      th{background:#f6f7f9;font-weight:600;white-space:nowrap}
    </style></head><body>";
}

// ------------------------------------------------------------
// Try to reach the database.
//
// If it is down we show a clear message on purpose. A blank
// white screen teaches you nothing; "cannot reach the database"
// tells you exactly which half of the system broke.
//
// (On a real production site you would log the reason and show
// the visitor something friendlier. Here we want to SEE it.)
// ------------------------------------------------------------
mysqli_report(MYSQLI_REPORT_OFF);          // we handle the error ourselves
$db = @new mysqli($DB_HOST, $DB_USER, $DB_PASS, $DB_NAME);

if ($db->connect_error) {
    // 503 = "the server is fine, something it depends on is not".
    // That is exactly the situation, so say so honestly.
    http_response_code(503);
    page_head("Scenario 5 - database down");
    echo "<div class='card'>";
    echo "<h1>Cannot reach the database</h1>";
    echo "<p class='down'>The web server is running. The database is not answering.</p>";
    echo "<p class='muted'>Reason reported by MySQL:<br><code>"
         . h($db->connect_error) . "</code></p>";
    echo "</div>";
    echo "<div class='card'><p class='muted'>";
    echo "This is the whole lesson of step 9. Nothing is wrong with this app ";
    echo "or with the server it runs on. Only the database went away. ";
    echo "You cannot even log in - the login form has no answers of its own, ";
    echo "it asks the same database. ";
    echo "A ticket that says &ldquo;the site is broken&rdquo; often looks exactly like this.";
    echo "</p></div></body></html>";
    exit;
}

// ------------------------------------------------------------
// Logging out is just throwing the session away.
// ------------------------------------------------------------
if (isset($_GET["logout"])) {
    $_SESSION = [];
    session_destroy();
    header("Location: " . strtok($_SERVER["REQUEST_URI"], "?"));
    exit;
}

// ------------------------------------------------------------
// Checking a password.
//
// The database never stores the password itself, only a hash of
// it. We hash what was typed and compare the two hashes.
//
//   $2y$...  = bcrypt, made by PHP's password_hash()  -> the real one
//   64 hex   = SHA2('...',256), made by MySQL itself  -> easy to type
//              at the mysql prompt in step 6, which is why it is here
//
// hash_equals compares in constant time, so the comparison does
// not leak how much of the hash was already correct.
// ------------------------------------------------------------
function password_matches($typed, $stored) {
    if (strlen($stored) > 0 && $stored[0] === "$") {   // bcrypt / argon
        return password_verify($typed, $stored);
    }
    return hash_equals(strtolower($stored), hash("sha256", $typed));
}

// ------------------------------------------------------------
// The login form posts back to this same page.
// ------------------------------------------------------------
$error = "";

if ($_SERVER["REQUEST_METHOD"] === "POST" && empty($_SESSION["user"])) {
    $username = trim($_POST["username"] ?? "");
    $password = $_POST["password"] ?? "";

    // Prepared statement, always. The username was typed by a stranger:
    // it is a VALUE to compare, never part of the SQL sentence.
    $stmt = $db->prepare("SELECT id, username, password_hash FROM users WHERE username = ? LIMIT 1");

    if (!$stmt) {
        $error = "The users table is missing - create it in step 6. <code>"
               . h($db->error) . "</code>";
    } else {
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $row = $stmt->get_result()->fetch_assoc();
        $stmt->close();

        if ($row && password_matches($password, $row["password_hash"])) {
            // A fresh session id on login, so any session id someone
            // already knew beforehand is worthless afterwards.
            session_regenerate_id(true);
            $_SESSION["user"] = $row["username"];
            header("Location: " . strtok($_SERVER["REQUEST_URI"], "?"));
            exit;
        }

        // One message for both failures on purpose. "No such user"
        // would tell a stranger which usernames exist.
        $error = "Wrong username or password.";
    }
}

// ============================================================
//  SCREEN 1 - not signed in yet
// ============================================================
if (empty($_SESSION["user"])) {
    page_head("Scenario 5 - Sign in");
    echo "<div class='card'>";
    echo "<h1>Sign in</h1>";
    echo "<p class='up'>&check; database connected</p>";
    echo "<p class='muted'>These credentials are not in this file. "
       . "They are rows in the <code>users</code> table.</p>";
    echo "<form method='post' autocomplete='off'>";
    echo "<label for='username'>Username</label>";
    echo "<input id='username' name='username' type='text' required autofocus value='"
       . h($_POST["username"] ?? "") . "'>";
    echo "<label for='password'>Password</label>";
    echo "<input id='password' name='password' type='password' required>";
    echo "<button type='submit'>Sign in</button>";
    if ($error !== "") { echo "<div class='err'>" . $error . "</div>"; }
    echo "</form>";
    echo "</div>";
    echo "<div class='card'><p class='muted'>";
    echo "The page is the same for everyone. Who may come in is decided by a row ";
    echo "in the database, not by the code.";
    echo "</p></div></body></html>";
    $db->close();
    exit;
}

// ============================================================
//  SCREEN 2 - signed in: show what is actually in the database
// ============================================================
page_head("Scenario 5 - Data");

echo "<div class='card'>";
echo "<div class='bar'><h1>Signed in as " . h($_SESSION["user"]) . "</h1>";
echo "<a href='?logout=1'>Sign out</a></div>";
echo "<p class='up'>&check; database connected</p>";
echo "<p class='muted'>Everything below was read out of <code>" . h($DB_NAME)
   . "</code> just now.</p>";
echo "</div>";

// Ask the database which tables exist. Even the list of tables is data.
$tables = [];
if ($list = $db->query("SHOW TABLES")) {
    while ($t = $list->fetch_array()) { $tables[] = $t[0]; }
}

if (!$tables) {
    echo "<div class='card'><p class='muted'>This database has no tables yet. "
       . "Create them in step 6 and reload.</p></div>";
}

foreach ($tables as $table) {
    // Table names come from SHOW TABLES, not from a visitor, but they are
    // still backticked so an odd name cannot break the query.
    $safe = "`" . str_replace("`", "``", $table) . "`";

    echo "<div class='card'>";
    echo "<h2>" . h($table) . "</h2>";

    $rows = $db->query("SELECT * FROM $safe LIMIT 50");

    if (!$rows) {
        echo "<p class='down'>Could not read this table.</p>";
        echo "<p class='muted'><code>" . h($db->error) . "</code></p>";
    } elseif ($rows->num_rows === 0) {
        echo "<p class='muted'>No rows yet. <code>INSERT</code> one and reload.</p>";
    } else {
        $cols = [];
        foreach ($rows->fetch_fields() as $f) { $cols[] = $f->name; }

        echo "<div class='scroll'><table><thead><tr>";
        foreach ($cols as $c) { echo "<th>" . h($c) . "</th>"; }
        echo "</tr></thead><tbody>";

        while ($r = $rows->fetch_assoc()) {
            echo "<tr>";
            foreach ($cols as $c) {
                $v = $r[$c];
                // A stored password hash never gets printed on a web page.
                if (preg_match("/pass|secret|token|hash/i", $c)) { $v = "********"; }
                echo "<td>" . ($v === null ? "<span class='muted'>NULL</span>" : h($v)) . "</td>";
            }
            echo "</tr>";
        }

        echo "</tbody></table></div>";
        echo "<p class='muted' style='margin-top:10px'>" . (int)$rows->num_rows
           . " row(s) shown (first 50).</p>";
    }
    echo "</div>";
}

echo "<div class='card'><p class='muted'>";
echo "Nothing on this page is written in the code. Add another row with ";
echo "<code>INSERT</code> and reload - the page changes and the code does not. ";
echo "Add a whole new table and a new section appears on its own. ";
echo "The page is not the data.";
echo "</p></div>";

echo "</body></html>";
$db->close();
