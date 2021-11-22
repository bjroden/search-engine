<!--      Start the HTML Page with a comment         -->
<!--      Print out the title, etc. and opening tags --> 
<html>
<head><title>Brian Roden's Search Engine</title></head>
<body>

<!--      Here comes the php portion of the page     -->
<?php

//------------------------------------------------------
// Now a php comment 
// This is the main program that either processes the form
// data or prints the form to capture data
//------------------------------------------------------
if (isset($_POST['stage']) && ($_POST['stage'] == 'process'))
{
   print_form();
   process_form();
}
else
{
   echo "<h2>Input search terms below</h2>";
   echo "<p>10 results are shown by default. You can optionally input a different number.</p>";
   print_form();
}
echo "<a id='fileList' href='files'>See full file list here</a>";

//------------------------------------------------------
// This is the function that prints the form
//------------------------------------------------------
function print_form()
{
echo <<<END
   <form action="$_SERVER[PHP_SELF]" method="post">
      <input type="Text" id="query" name="query" placeholder="Search Terms" align="TOP" size="20">
      <input type="number" id="numresults" name="numresults" min="1" placeholder= "#" align="MIDDLE">
      <input type="hidden" name="stage" value="process">
      <input type="Submit" id="submit" name="submit" value="Search" align="MIDDLE">
   </form>
END;
}

//------------------------------------------------------
// This is the function that processes the form data
//------------------------------------------------------
function process_form()
{
   echo "<h2>Search: " . $_POST[query] . "</h2>";
   echo "<table id='results'>";
   if (!empty($_POST['numresults']))
   {
      echo shell_exec("./run_query.sh -n " . escapeshellarg($_POST[numresults]) . " " . escapeshellarg($_POST[query])); 
   }
   else
   {
      echo shell_exec("./run_query.sh " . escapeshellarg($_POST[query])); 
   }
   echo "</table>";
}

?>
</body>
</html>

<style>
body {
    color: #444;
    background-color: #EEE;
    margin: 40px auto;
    max-width: 650px;
    line-height: 1.6em;
    font-size: 18px;
    padding: 0;
    text-align: center;
}

#results {
    font-size: 30px;
    margin-left: auto;
    margin-right: auto;
    border-spacing: 10px;
}

#resultlink:hover {
    color: red;
}

#query {
    color: #444;
    border: none;
    background: #a3acb5;
    padding: 15px;
    border-radius: 25px;
    transition: all 0.3s ease 0s;
    font-size: 18px;
}

#query:hover {
    background: #d8dde6;
}
#submit {
    color: #444;
    padding: 15px;
    border: none;
    background: #91bce6;
    border-radius: 25px;
    transition: all 0.3s ease 0s;
    font-size: 18px;
}

#submit:hover {
    color: white;
    background-color: red;
}

#fileList {
    bottom: 0%;
    margin: 40px auto;
    height: 40px;
    font-size: 20px;
    text-align: center;
}

#fileList:hover {
    color: red;
}

#numresults {
    color: #444;
    border: none;
    background: #a3acb5;
    padding: 15px;
    border-radius: 25px;
    width: 80px;
    transition: all 0.3s ease 0s;
    font-size: 18px;
    text-align: center;
}

#numresults:hover {
    background: #d8dde6;
}

::placeholder {
    color: #525252;
}

input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
}

input[type=number] {
    -moz-appearance: textfield;
}

</style>
