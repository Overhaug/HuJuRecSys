
<style type="text/css">

h1.likert-header {
  padding-left:4.25%;
  margin:20px 0 0;
}
form .statement {
  display:block;
  font-size: 14px;
  font-weight: bold;
  padding: 30px 0 0 4.25%;
  margin-bottom:10px;
}
form .likert2 {
  list-style:none;
  width:100%;
  margin:0;
  padding:0 0 0px;
  display:block;
  border-bottom:2px solid #efefef;
}
form .likert2:last-of-type {border-bottom:0;}
form .likert2:before {
  content: '';
  position:relative;
  top:11px;
  left:0%;
  display:block;
  background-color:#efefef;
  height:4px;
  width:77%;
}
form .likert2 li {
  display:inline-block;
  width:15%;
  text-align:center;
  vertical-align: top;
}
form .likert2 li input[type=radio] {
  display:block;
  position:relative;
  top:0;
  left:50%;
  margin-left:-6px;
  
}
form .likert li label {width:100%;}
form .buttons {
  margin:30px 0;
  padding:0 4.25%;
  text-align:right
} 
form .buttons button {
  padding: 5px 10px;
  background-color: #67ab49;
  border: 0;
  border-radius: 3px;
} </style>


<style type="text/css">
h1.likert-header {
  padding-left:4.25%;
  margin:20px 0 0;
}
form .statement {
  display:block;
  font-size: 14px;
  font-weight: bold;
  padding: 30px 0 0 4.25%;
  margin-bottom:10px;
}
form .likert {
  list-style:none;
  width:100%;
  margin:0;
  padding:0 0 0px;
  display:block;
  /* border-bottom:2px solid #efefef;*/
}
form .likert:last-of-type {border-bottom:0;}
form .likert:before {
  content: '';
  position:relative;
  top:11px;
  left:0%;
  display:block;
  background-color:#efefef;
  height:4px;
  width:75%;
}
form .likert li {
  display:inline-block;
  width:18%;
  text-align:center;
  vertical-align: top;
}
form .likert li input[type=radio] {
  display:block;
  position:relative;
  top:0;
  left:50%;
  margin-left:-6px;
  
}
form .likert li label {width:100%;}
form .buttons {
  margin:30px 0;
  padding:0 4.25%;
  text-align:right
} 
form .buttons button {
  padding: 5px 10px;
  background-color: #67ab49;
  border: 0;
  border-radius: 3px;
}


.jumbotron {
  padding: 2rem 2rem;
}

.text {
  height: 200px;
  overflow: hidden;
}
.text-container {
  position: relative;
}
.text-container label {
  position: absolute;
  top: 100%;
  width: 100%;
}
.text-container input {
  display: none;
}
.text-container label:after {
  content: "Show More";
  text-decoration: underline;
  color: green;
}
.text-container input:checked + label:after {
  content: "Show Less";
  color: gray;
}
.text-container input:checked ~ div {
  height: 100%;
}

.text2 {
  height: 200px;
  overflow: hidden;
}
.text-container2 {
  position: relative;
}
.text-container2 label {
  position: absolute;
  top: 100%;
  width: 100%;
}
.text-container2 input {
  display: none;
}
.text-container2 label:after {
  content: "Show More";
  text-decoration: underline;
  color: green;
}
.text-container2 input:checked + label:after {
  content: "Show Less";
  color: gray;
}
.text-container2 input:checked ~ div {
  height: 100%;
}
.separator {
  border-bottom-style: solid;
  border-width: 3px;
  margin-bottom: 15px;
}
.grey-color {
  color: #666;
}

</style>

<script language="javascript" type="text/javascript">

  function checkedRadioBtn(sGroupName)
  {   
    var group = document.getElementsByName(sGroupName);
    for ( var i = 0; i < group.length; i++) {
      if (group.item(i).checked) {

        return true;
      } else if (group[0].type !== 'radio') {
                //if you find any in the group not a radio button return null
                return null;
              }
            }
            return false;
          }

          function checkForm() {
            if(checkedRadioBtn("sim") &&
              checkedRadioBtn("fam1") && checkedRadioBtn("fam2") && checkedRadioBtn("conf"))  {
              document.demo_form.action = "index.php";
            document.demo_form.submit();
          } else {
            alert('Please checked that you have responded to the question!');
          }
        }
      </script>



      <div>

        <form id="demo_form" name="demo_form" action="index.php" method="GET">
          <?php 

          $r1 = $_SESSION[$SURVEYLINK]['pairs'][$_GET["step"]-1][0];
          $r2 = $_SESSION[$SURVEYLINK]['pairs'][$_GET["step"]-1][1];
    // recipe	title	avg_rating	ratings	image	directions	ing
// movie	title	cover_path	overview	actors	genres	release_date	directors
          $r1_subcategory = $_SESSION[$SURVEYLINK]['data'][$r1][0];
          $r2_subcategory = $_SESSION[$SURVEYLINK]['data'][$r2][0];

          $r1_title = $_SESSION[$SURVEYLINK]['data'][$r1][1];
          $r2_title =  $_SESSION[$SURVEYLINK]['data'][$r2][1];

          $r1_image = $_SESSION[$SURVEYLINK]['data'][$r1][2];
          $r2_image =  $_SESSION[$SURVEYLINK]['data'][$r2][2];

          $r1_image_caption = $_SESSION[$SURVEYLINK]['data'][$r1][3];
          $r2_image_caption =  $_SESSION[$SURVEYLINK]['data'][$r2][3];

          $r1_author = $_SESSION[$SURVEYLINK]['data'][$r1][4];
          $r2_author = $_SESSION[$SURVEYLINK]['data'][$r2][4];

          $r1_datetime = $_SESSION[$SURVEYLINK]['data'][$r1][7];
          $r2_datetime =  $_SESSION[$SURVEYLINK]['data'][$r2][7];

          $r1_text = $_SESSION[$SURVEYLINK]['data'][$r1][8];
          $r2_text =  $_SESSION[$SURVEYLINK]['data'][$r2][8];

          $r1_auth_bio = $_SESSION[$SURVEYLINK]['data'][$r1][9];
          $r2_auth_bio =  $_SESSION[$SURVEYLINK]['data'][$r2][9];
          ?>


          <div align="center">

            <div align="center">
             <p class="lead">
               <h1>[Question <?php echo $_GET["step"] ?> / 10]</h1>
               <h2>To what extent are the two news articles shown below similar?</h2>

             </p>
           </div>


           <!-- <label class="statement">The two recipes presented above are:</label> -->
           <ul class='likert'>
            <li>
              <input type="radio" name="sim" value="1">
              <label>1 </br>(Completely different) </label>
            </li>
            <li>
              <input type="radio" name="sim" value="2">
              <label>2 </label>
            </li>
            <li>
              <input type="radio" name="sim" value="3">
              <label>3</label>
            </li>
            <li>
              <input type="radio" name="sim" value="4">
              <label>4</label>
            </li>
            <li>
              <input type="radio" name="sim" value="5">
              <label>5 </br>(They are more or less the same)</label>
            </li>
          </ul>


          <p> (Scroll to the end of page to get to the next question)</p>
        </div>

        <?php
        function format_authors($items) {
          $author_list = explode(";", $items);
          $author_list = array_filter($author_list);
          $authors = "";
          for ($i = 0; $i < count($author_list); $i++) {
            if (count($author_list) == 2) {
              $authors .= "<strong>".$author_list[0]."</strong>"." and <strong>".$author_list[1]."</strong>";
              break;
            }
            elseif (count($author_list) == 1) {
              $authors .= "<strong>".$author_list[$i]."</strong>";
              break;
            }
            elseif ($i == count($author_list)-1) {
              $authors .= "and <strong>".$author_list[$i]."</strong>";
            }
            else {
              $authors .= "<strong>".$author_list[$i]."</strong>, ";
            }
          }
          return $authors;
        }
        ?>


        <div class="row jumbotron">


          <div class="col" style="background-color: #fcf8e3; padding-bottom: 10px;">
            <div class="separator">
              <h1>News 1</h1>
            </div>
            <span><strong><?php echo $r1_subcategory ?></strong></span>
            <h3><?php echo $r1_title?></h3>
            <img style="max-width: 500px;" src="<?php echo '/'.$SURVEYLINK.'/images'.$r1_image; ?>"; class="img-fluid" title="<?php echo $r1_image?>">
            <p class="grey-color">
              <?php 
              echo $r1_image_caption;
              ?>
          </p>
          <p class="grey-color">By <?php
            $r1_authors = format_authors($r1_author);
            echo $r1_authors;
            ?></p>
          <p class="grey-color"><?php echo $r1_datetime ?></p>
          <div class="text-container">
            <input id="ch" type="checkbox">
            <label for="ch"></label>
            <div class="text" style="font-size: 18px">
            <?php 
            if ($_SESSION[$SURVEYLINK]['random'] == $_GET["step"]) {
              echo "IF YOU READ THIS TEXT THEN PLEASE RATE ALL ANSWERS TO THIS QUESTION WITH A 5, SO THAT WE KNOW YOU ANSWER THE QUESTIONS CAREFULLY. ";
            } else {
              echo $r1_text;
              $r1_author_bios = explode("<br><br>", $r1_auth_bio);
              $r1_author_bios = array_filter($r1_author_bios);
              $r1_authors_unformatted = explode(";", $r1_author);
              $r1_bios = "";
              for ($i = 0; $i < count($r1_author_bios); $i++) {
                $r1_bios .= "<strong>".$r1_authors_unformatted[$i]."</strong><br>".$r1_author_bios[$i]."<br>";
              }
              echo $r1_bios;
            }
            ?> </p>
          </div>
          </div>
          
        </div>

        <div class="col" style="background-color: #bcdff1; padding-bottom: 10px;">
          <div class="separator">
            <h1>News 2</h1>
          </div>
          <span><strong><?php echo $r2_subcategory ?></strong></span>
          <h3><?php echo $r2_title?></h3>
          <img style="max-width: 500px;" src="<?php echo '/'.$SURVEYLINK.'/images'.$r2_image; ?>"; class="img-fluid" title="<?php echo $r2_image?>">
          <p class="grey-color">
            <?php 
            echo $r2_image_caption;
            ?>
        </p>
        <p class="grey-color">By <?php
          $r2_authors = format_authors($r2_author);
          echo $r2_authors; 
         ?></p>
        <p class="grey-color"><?php echo $r2_datetime ?></p>
        <div class="text-container2">
          <input id="ch2" type="checkbox">
          <label for="ch2"></label>
          <div class="text2" style="font-size: 18px">
            <?php 
            if ($_SESSION[$SURVEYLINK]['random'] == $_GET["step"]) {
              echo "IF YOU READ THIS TEXT THEN PLEASE RATE ALL ANSWERS TO THIS QUESTION WITH A 5, SO THAT WE KNOW YOU ANSWER THE QUESTIONS CAREFULLY. ";
            } else {
              echo $r2_text;
              $r2_author_bios = explode("<br><br>", $r2_auth_bio);
              $r2_author_bios = array_filter($r2_author_bios);
              $r2_authors_unformatted = explode(";", $r2_author);
              $r2_bios = "";
              for ($i = 0; $i < count($r2_author_bios); $i++) {
                $r2_bios .= "<strong>".$r2_authors_unformatted[$i]."</strong><br>".$r2_author_bios[$i]."<br>";
              }
              echo $r2_bios;
            }
            ?> </p>
          </div>
        </div>
      </p>


    </div>



  </div>

  <div align="center">
   <h2>Please complete the questionnaire below!</h2>
   <hr>

          <!-- <h5>To what extent do you agree with the following statements:</h5>

I looked at the <b>movie title</b> to estimate the similarity between the movies:
<ul class='likert'>
      <li>
        <input type="radio" name="title" value="1">
        <label>1 <br>(Totally Disagree)</label>
      </li>
      <li>
        <input type="radio" name="title" value="2">
        <label>2</label>
      </li>
      <li>
        <input type="radio" name="title" value="3">
        <label>3</label>
      </li>
      <li>
        <input type="radio" name="title" value="4">
        <label>4</label>
      </li>
      <li>
        <input type="radio" name="title" value="5">
        <label>5 <br>(Totally Agree)</label>
      </li>
    </ul>

I looked at the <b>movie image</b> to estimate the similarity between the movies:
<ul class='likert'>
      <li>
        <input type="radio" name="image" value="1">
        <label>1 <br>(Totally Disagree)</label>
      </li>
      <li>
        <input type="radio" name="image" value="2">
        <label>2</label>
      </li>
      <li>
        <input type="radio" name="image" value="3">
        <label>3</label>
      </li>
      <li>
        <input type="radio" name="image" value="4">
        <label>4</label>
      </li>
      <li>
        <input type="radio" name="image" value="5">
        <label>5 <br>(Totally Agree)</label>
      </li>
    </ul>

I looked at the <b>plot text</b> to estimate the similarity between the movies:
<ul class='likert'>
      <li>
        <input type="radio" name="overview" value="1">
        <label>1 <br>(Totally Disagree)</label>
      </li>
      <li>
        <input type="radio" name="overview" value="2">
        <label>2</label>
      </li>
      <li>
        <input type="radio" name="overview" value="3">
        <label>3</label>
      </li>
      <li>
        <input type="radio" name="overview" value="4">
        <label>4</label>
      </li>
      <li>
        <input type="radio" name="overview" value="5">
        <label>5 <br>(Totally Agree)</label>
      </li>
    </ul>


I looked at the <b>genre</b> to estimate the similarity between the movies:
<ul class='likert'>
      <li>
        <input type="radio" name="genre" value="1">
        <label>1 <br>(Totally Disagree)</label>
      </li>
      <li>
        <input type="radio" name="genre" value="2">
        <label>2</label>
      </li>
      <li>
        <input type="radio" name="genre" value="3">
        <label>3</label>
      </li>
      <li>
        <input type="radio" name="genre" value="4">
        <label>4</label>
      </li>
      <li>
        <input type="radio" name="genre" value="5">
        <label>5 <br>(Totally Agree)</label>
      </li>
    </ul>
    
    
    I looked at the <b>director(s)</b> to estimate the similarity between the movies:
<ul class='likert'>
      <li>
        <input type="radio" name="director" value="1">
        <label>1 <br>(Totally Disagree)</label>
      </li>
      <li>
        <input type="radio" name="director" value="2">
        <label>2</label>
      </li>
      <li>
        <input type="radio" name="director" value="3">
        <label>3</label>
      </li>
      <li>
        <input type="radio" name="director" value="4">
        <label>4</label>
      </li>
      <li>
        <input type="radio" name="director" value="5">
        <label>5 <br>(Totally Agree)</label>
      </li>
    </ul>
    
    I looked at the <b>release date</b> to estimate the similarity between the movies:
<ul class='likert'>
      <li>
        <input type="radio" name="date" value="1">
        <label>1 <br>(Totally Disagree)</label>
      </li>
      <li>
        <input type="radio" name="date" value="2">
        <label>2</label>
      </li>
      <li>
        <input type="radio" name="date" value="3">
        <label>3</label>
      </li>
      <li>
        <input type="radio" name="date" value="4">
        <label>4</label>
      </li>
      <li>
        <input type="radio" name="date" value="5">
        <label>5 <br>(Totally Agree)</label>
      </li>
    </ul>
    
    I looked at the <b>stars</b> to estimate the similarity between the movies:
<ul class='likert'>
      <li>
        <input type="radio" name="cast" value="1">
        <label>1 <br>(Totally Disagree)</label>
      </li>
      <li>
        <input type="radio" name="cast" value="2">
        <label>2</label>
      </li>
      <li>
        <input type="radio" name="cast" value="3">
        <label>3</label>
      </li>
      <li>
        <input type="radio" name="cast" value="4">
        <label>4</label>
      </li>
      <li>
        <input type="radio" name="cast" value="5">
        <label>5 <br>(Totally Agree)</label>
      </li>
    </ul>
    
     <hr>
   -->
   <h5>To what extent are you familiar with News 1 shown above:</h5>

   <ul class='likert'>
    <li>
      <input type="radio" name="fam1" value="1">
      <label>1 <br>(Not at all)</label>
    </li>
    <li>
      <input type="radio" name="fam1" value="2">
      <label>2</label>
    </li>
    <li>
      <input type="radio" name="fam1" value="3">
      <label>3</label>
    </li>
    <li>
      <input type="radio" name="fam1" value="4">
      <label>4</label>
    </li>
    <li>
      <input type="radio" name="fam1" value="5">
      <label>5 <br>(Very familiar)</label>
    </li>
  </ul>

  <h5>To what extent are you familiar with News 2 shown above:</h5>

  <ul class='likert'>
    <li>
      <input type="radio" name="fam2" value="1">
      <label>1 <br>(Not at all)</label>
    </li>
    <li>
      <input type="radio" name="fam2" value="2">
      <label>2</label>
    </li>
    <li>
      <input type="radio" name="fam2" value="3">
      <label>3</label>
    </li>
    <li>
      <input type="radio" name="fam2" value="4">
      <label>4</label>
    </li>
    <li>
      <input type="radio" name="fam2" value="5">
      <label>5 <br>(Very familiar)</label>
    </li>
  </ul>

  <h5>On a scale of 1-5, how confident are you of your provided similarity rating:</h5>

  <ul class='likert'>
    <li>
      <input type="radio" name="conf" value="1">
      <label>1 <br>(Not at all)</label>
    </li>
    <li>
      <input type="radio" name="conf" value="2">
      <label>2</label>
    </li>
    <li>
      <input type="radio" name="conf" value="3">
      <label>3</label>
    </li>
    <li>
      <input type="radio" name="conf" value="4">
      <label>4</label>
    </li>
    <li>
      <input type="radio" name="conf" value="5">
      <label>5 <br>(Absolutely confident)</label>
    </li>
  </ul>






</div>

<hr />


<div align="center">
  <input type="hidden" id="user_id" name="user_id" value="<?php echo session_id() ?>" />
  <?php 
// MOST IMPORTANT VARIABLE TO SET HERE
  if (intval($_GET["step"]) < $COUNTER) {
    ?>
    <input type="hidden" name="next_step" value="survey" />

  <?php } else { ?>
    <input type="hidden" name="next_step" value="demo" />
  <?php }?>
  <input type="hidden" name="step" value="<?php echo $_GET["step"]+1 ?>" />
  <input type="hidden" name="pair" value="<?php echo $r1.";".$r2 ?>" />

  <input type="hidden" name="survey_id" value="<?php echo $SID ?>" />

  <button type="button" class="btn btn-lg btn-success" onclick="javascript:checkForm();">Next >> </button>

</div>
</form>

</div>
<br />
<br />
