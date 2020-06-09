<div class="jumbotron">
<div align="center">
	<h2>Welcome to the "Online News Similarity" Survey</h2>
	</div>
	
	
	<p class="lead">
	You are invited to take part in a research survey about news.  
	In this survey you will see 10 random news pairs. On a scale from 1 to 5, you will then evaluate 
	how similar the news are. Furthermore, you will be asked how familiar you are with the two news and about your 
	similarity estimate confidence. Below you can see a screenshot of what the study looks like.
	</p>
	
		<div align="center">
	<figure class="figure">
  <img src="new_example.png" class="figure-img img-fluid rounded" alt="Example survey.">
  <figcaption class="figure-caption">Example survey.</figcaption>
	</figure>
	</div>
	
	
	<p class="lead">
	Your participation will require approximately 5-10 minutes and 
	is completed online at your computer. At the end of the survey, we will also ask you some demographic questions.  
	
	There are no known risks or discomforts associated with this survey. 
	Taking part in this study is completely voluntary. If you choose not to be in the study 
	you can withdraw at any time.</p>
	<p class="lead">
	Your responses will be kept strictly confidential, and digital data will be stored in secure data files.  
	Any report of this research that is made available to the public will not 
	include your name or any other individual information by which you could be identified.  
	If you have questions or want a copy or summary of this study’s results, you can contact 
	the researcher at the email address below. </p>
	<p class="lead">
	Please feel free to print a copy of this consent page to keep for your records.
	Clicking the "Start Survey!" button below indicates that you are 18 years of age or older, 
	and indicates your consent to participate in this survey. </p>
	<p class="lead">
	Contact: Assoc. Prof. Dr. Christoph Trattner, University of Bergen, Norway. </br>
	Email: <a href="mailto:christoph.trattner@uib.no">christoph.trattner@uib.no</a></br></br>
	</p>
	
	<p>
	<div align="center">
	
	
	
	<form id="demo_form" name="demo_form" action="index.php" method="GET">
		<input type="hidden" id="user_id" name="user_id" value="<?php echo session_id() ?>" />
<input type="hidden" name="next_step" value="survey" />
<input type="hidden" name="step" value="1" />
<input type="hidden" name="survey_id" value="<?php echo $SID ?>" />
<button type="submit" class="btn btn-lg btn-success" >Start Survey!</button>
</div>
</form>
	</p>
</div>