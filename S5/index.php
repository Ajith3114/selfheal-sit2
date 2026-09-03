<?php
// ============================================================
//  6F School of IT - Scenario 5
//  "Where does the data on this page come from?"
//
//  This whole app is one page. It asks the database for rows
//  and prints them. That is all it does.
//
//  EDIT THE THREE LINES BELOW, then save. Nothing else.
//  Put this file at:  /var/www/html/index.php
// ============================================================

$DB_HOST = "YOUR-ENDPOINT.rds.amazonaws.com";   // from step 4 of steps.txt
$DB_USER = "admin";
$DB_PASS = "YOUR-PASSWORD";
$DB_NAME = "workshop";

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

header("Content-Type: text/html; charset=utf-8");
echo "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>";
echo "<meta name='viewport' content='width=device-width,initial-scale=1'>";
echo "<title>Scenario 5 - Messages</title>";
echo "<style>
  body{font:16px/1.6 system-ui,-apple-system,'Segoe UI',sans-serif;
       max-width:640px;margin:0 auto;padding:40px 20px;color:#1a1d21;background:#f6f7f9}
  .card{background:#fff;border:1px solid #e3e6ea;border-radius:12px;padding:24px;margin-bottom:16px}
  h1{margin:0 0 4px;font-size:24px}
  .muted{color:#5c6570;font-size:14px;margin:0}
  .up{color:#1a7f4b;font-weight:600}
  .down{color:#b52f4a;font-weight:600}
  ul{margin:12px 0 0;padding-left:20px} li{margin-bottom:8px}
  code{background:#f6f7f9;border:1px solid #e3e6ea;border-radius:4px;padding:2px 6px;font-size:14px}
</style></head><body>";

if ($db->connect_error) {
    // 503 = "the server is fine, something it depends on is not".
    // That is exactly the situation, so say so honestly.
    http_response_code(503);
    echo "<div class='card'>";
    echo "<h1>Cannot reach the database</h1>";
    echo "<p class='down'>The web server is running. The database is not answering.</p>";
    echo "<p class='muted'>Reason reported by MySQL:<br><code>"
         . htmlspecialchars($db->connect_error) . "</code></p>";
    echo "</div>";
    echo "<div class='card'><p class='muted'>";
    echo "This is the whole lesson of step 8. Nothing is wrong with this app ";
    echo "or with the server it runs on. Only the database went away. ";
    echo "A ticket that says &ldquo;the site is broken&rdquo; often looks exactly like this.";
    echo "</p></div></body></html>";
    exit;
}

// ------------------------------------------------------------
// Connected. Read the rows and print them.
// ------------------------------------------------------------
echo "<div class='card'>";
echo "<h1>Messages</h1>";
echo "<p class='up'>&check; database connected</p>";

$rows = $db->query("SELECT text FROM messages ORDER BY id DESC");

if (!$rows) {
    echo "<p class='down'>Connected, but the query failed.</p>";
    echo "<p class='muted'><code>" . htmlspecialchars($db->error) . "</code><br>";
    echo "Did you create the table in step 6?</p>";
} elseif ($rows->num_rows === 0) {
    echo "<p class='muted'>The table is empty. Insert a row in step 6 and reload.</p>";
} else {
    echo "<ul>";
    while ($r = $rows->fetch_assoc()) {
        // htmlspecialchars: whatever is in the database is text, not HTML.
        echo "<li>" . htmlspecialchars($r["text"]) . "</li>";
    }
    echo "</ul>";
}
echo "</div>";

echo "<div class='card'><p class='muted'>";
echo "Nothing on this page is written in the code. Add another row with ";
echo "<code>INSERT</code> and reload - the page changes and the code does not. ";
echo "The page is not the data.";
echo "</p></div>";

echo "</body></html>";
$db->close();
