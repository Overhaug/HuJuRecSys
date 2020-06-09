<div class="jumbotron">
<div align="center">

<script>
function myFunction() {
	  /* Get the text field */
	  var copyText = document.getElementById("myInput");

	  /* Select the text field */
	  copyText.select();

	  /* Copy the text inside the text field */
	  document.execCommand("copy");

	  /* Alert the copied text */
	  alert("Copied the text: " + copyText.value);
	}
</script>

	<h2>Thank you for your participation in this survey :)</h2>
	</br>
	<p class="lead">
	Please copy & paste the code below to Amazon Mechanical Turk in order to obtain your payment for this HIT!
	
	<!-- The text field -->
	<div class="col-8">
<input type="text" class="form-control" value="<?php echo $_SESSION[$SURVEYLINK]['survey'] ?>" id="myInput"><button type="submit" class="btn btn-primary mb-2" onclick="myFunction()">Copy!</button>
	</div>

		<!--  If you want to take the survey again (with different data), then click the "Restart Survey!" button below.
		
		<form id="demo_form" name="demo_form" action="index.php" method="POST">
			<input type="hidden" id="user_id" name="user_id" value="<?php echo session_id() ?>" />
			<input type="hidden" name="next_step" value="" />
			<button type="submit" class="btn btn-lg btn-success" >Restart Survey!</button>
		</form>
		-->
	</p>
	</div>
</div>

<?php 
// Unset all of the session variables.
/*$_SESSION[$SURVEYLINK] = array();

// If it's desired to kill the session, also delete the session cookie.
// Note: This will destroy the session, and not just the session data!
if (ini_get("session.use_cookies")) {
    $params = session_get_cookie_params();
    setcookie(session_name(), '', time() - 42000,
        $params["path"], $params["domain"],
        $params["secure"], $params["httponly"]
        );
}

// Finally, destroy the session.
session_destroy();*/
?>