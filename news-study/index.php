
<?php

static $COUNTER = 10;
static $SID = "5b4126d935hjd0gv1000001x";
static $SURVEYLINK = "news-study";
static $MAX_HITS = 100;
static $SESSION_TIME = 1;// in hours
static $STUDY = "news-study";

ini_set('display_errors', 1);
error_reporting(E_ALL);

include_once("sync.php");
include_once("Logging.php");


// server should keep session data for AT LEAST 2 hour
session_name($STUDY);
ini_set('session.gc_maxlifetime', 3600*$SESSION_TIME);

// each client should remember their session id for EXACTLY 2 hour
session_set_cookie_params(3600*$SESSION_TIME);
session_start();

/*if (!isset($_SESSION[$SURVEYLINK]['discard_afterx'])) {
 session_unset();
 session_destroy();
 session_start();
 echo "out1";
}*/

// JS console log
function console_log( $data ){
  echo '<script>';
  echo 'console.log('. json_encode( $data ) .')';
  echo '</script>';
}


// DELETE SESSION AFTER 2 HOURS and start a new one - issue is old session may exist longer on server:)
// muh
$now = time();
if (isset($_SESSION[$SURVEYLINK]['discard_afterx']) && $now > $_SESSION[$SURVEYLINK]['discard_afterx']) {
    // this session has worn out its welcome; kill it and start a brand new one
    session_unset();
    session_destroy();
    //session_set_cookie_params(3600*$SESSION_TIME);
    session_start();
    // echo "out2";
}

$_SESSION[$SURVEYLINK]['discard_afterx'] = $now + 3600*$SESSION_TIME;

//print_r(session_get_cookie_params());


$obj = new Synchro($_SERVER['DOCUMENT_ROOT']."/".$SURVEYLINK."/sync/data.sync");
//$obj->pairs = 'world'.$obj->hello;


if ($obj->pairs == null) {
    $pairs = array();
    $file = fopen($_SERVER['DOCUMENT_ROOT'].'/'.$SURVEYLINK.'/pairs_2000-quantile-sample.csv', 'r');
    while (($line = fgetcsv($file,0, "\t")) !== FALSE) {
        //$line is an array of the csv elements
        array_push($pairs,$line);
    }
    fclose($file);
    shuffle($pairs);
    $obj->pairs = $pairs;
    
    //print_r($paris)
} else {
    //echo "is set";
}


if ($obj->data == null) {
    $data = array();
    $file = fopen($_SERVER['DOCUMENT_ROOT'].'/'.$SURVEYLINK.'/data_new.csv', 'r');
    while (($line = fgetcsv($file,0, "\t")) !== FALSE) {
        //$line is an array of the csv elements
        //  array_push($_SESSION[$SURVEYLINK]['data'],$line);

        $dat = array();
        for ($i=1; $i < count($line);$i++) {
            array_push($dat,$line[$i]);
        }
        $data[$line[0]] = $dat;
        
    }
    fclose($file);
   // print_r($data);
    
    $obj->data = $data;
}else {
    //echo "is set";
}


include_once("Logging.php");



// Start the session
//if(session_id() == '') {
  //  session_start();
//}

// Logging class initialization
if (!isset($_SESSION[$SURVEYLINK]['log'])) {
    $_SESSION[$SURVEYLINK]['log'] = new Logging();
    $_SESSION[$SURVEYLINK]['survey'] = uniqid().'-'.session_id();
    $_SESSION[$SURVEYLINK]['log']->lfile($_SERVER['DOCUMENT_ROOT'].'/'.$SURVEYLINK.'/logs/'.$_SESSION[$SURVEYLINK]['survey'].'-logfile.txt');
    
   // $_SESSION[$SURVEYLINK]['log']->lfile($_SERVER['DOCUMENT_ROOT'].'/survey/logfile.txt');
}

if (!isset($_SESSION[$SURVEYLINK]['random'])) {
    $_SESSION[$SURVEYLINK]['random'] = rand ( 1 , 10 );
}


function test_input($data) {
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
}

//echo $_SESSION[$SURVEYLINK]['survey'];

//echo "hm".$obj->counter;

?>



<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="author" content="Christoph Trattner">

    <title>News Survey</title><!-- page title -->

    <link href="css/bootstrap.min.css" rel="stylesheet">
    <link href="css/bootstrap-grid.css" rel="stylesheet">

    <link href="css/font-awesome-4.7.0/css/font-awesome.min.css" rel="stylesheet">


    <!-- jQuery Version 1.11.1 -->
    <script src="js/jquery.js"></script>

    <!-- Bootstrap Core JavaScript -->
    <script src="js/tether.min.js"></script>
    <script src="js/bootstrap.min.js"></script>

</head>

<body>

    <!-- Page Content -->

    <div class="container">

        <?php 

        $show_survey = false;

        if (isset($_GET["survey_id"])) {
            if($_GET["survey_id"] == $SID) {
                $show_survey = true;
            }

        }



        $next_step = "";

        if (isset($_GET["next_step"])) {
            $next_step = $_GET["next_step"];
        }


        if ($show_survey == true) {
            if ($next_step == "survey") {


                if (!isset($_SESSION[$SURVEYLINK]['data']) && !isset($_SESSION[$SURVEYLINK]['pairs'])) {

                    $counter = 0;

                    if ($obj->counter==null) {
                        $counter = $obj->counter = 1;
         //   echo "FUCK2".$obj->counter;
                    } else {
                        $counter = $obj->counter = $obj->counter+$COUNTER;

            //echo $obj->counter;
                    }
                    $counter = $counter-1;
                    $data = (array)$obj->data;
                    $pairs = (array)$obj->pairs;



                    $j = 0;
                    for ($i = $counter; $i < $counter+$COUNTER;$i++) {
                        $_SESSION[$SURVEYLINK]['pairs'][$j] = $pairs[$i];

                        $r1 = $_SESSION[$SURVEYLINK]['pairs'][$j][0];
                        $r2 = $_SESSION[$SURVEYLINK]['pairs'][$j][1];   

                        $_SESSION[$SURVEYLINK]['data'][$r1] = $data[$r1];
                        $_SESSION[$SURVEYLINK]['data'][$r2] = $data[$r2];
                        $j++;

                    } 
                }

   // if (!isset($_SESSION[$SURVEYLINK]['step'])) {
   //     $_SESSION[$SURVEYLINK]['step'] = 1;
   // } else {
   //     $_SESSION[$SURVEYLINK]['step'] = $_SESSION[$SURVEYLINK]['step']+1;
   // }

                $sim = "NA";
                $pair = "NA";

   /* $title = "NA";
    $image = "NA";
    
    $overview = "NA";
    $genre = "NA";
    $director = "NA";
    $date = "NA";
    $cast = "NA";*/
    
    $fam1 = "NA";
    $fam2 = "NA";
    $conf = "NA";
    
    if (isset($_GET["sim"])) {
        $sim = $_GET["sim"];
    }
    if (isset($_GET["pair"])) {
        $pair = $_GET["pair"];
    }
    
   /* if (isset($_GET["title"])) {
        $title = $_GET["title"];
    }
    if (isset($_GET["image"])) {
        $image = $_GET["image"];
    }
    if (isset($_GET["overview"])) {
        $overview = $_GET["overview"];
    }
    if (isset($_GET["genre"])) {
        $genre = $_GET["genre"];
    }
    if (isset($_GET["director"])) {
        $director = $_GET["director"];
    }
    if (isset($_GET["date"])) {
        $date = $_GET["date"];
    }
    if (isset($_GET["cast"])) {
        $cast = $_GET["cast"];
    }*/
    if (isset($_GET["fam1"])) {
        $fam1 = $_GET["fam1"];
    }
    if (isset($_GET["fam2"])) {
        $fam2 = $_GET["fam2"];
    }
    if (isset($_GET["conf"])) {
        $conf = $_GET["conf"];
    }
    
    if ($_GET["step"] == 1) {
    } else {
        $_SESSION[$SURVEYLINK]['log']->lwrite("survey","user\t".session_id().
            "\tsim\t".$sim.
            "\tpair\t".$pair.
          /*  "\ttitle\t".$title.
            "\timage\t".$image.
            "\toverview\t".$overview.
            "\tgenre\t".$genre.
            "\tdirector\t".$director.
            "\tdate\t".$date.
            "\tcast\t".$cast.*/
            "\tfam1\t".$fam1.
            "\tfam2\t".$fam2.
            "\tconf\t".$conf.
            "\trandom\t".$_SESSION[$SURVEYLINK]['random'].
            "\tstep\t".(intval($_GET["step"])-1)
        );
        $_SESSION[$SURVEYLINK]['log']->lclose(); 
    }
    require("survey.php");
    
} else if ($next_step == "demo") {

    $sim = "NA";
    $pair = "NA";
    
   /* $title = "NA";
    $image = "NA";
    
    $overview = "NA";
    $genre = "NA";
    $director = "NA";
    $date = "NA";
    $cast = "NA";*/
    
    $fam1 = "NA";
    $fam2 = "NA";
    $conf = "NA";
    
    if (isset($_GET["sim"])) {
        $sim = $_GET["sim"];
    }
    if (isset($_GET["pair"])) {
        $pair = $_GET["pair"];
    }
    
   /* if (isset($_GET["title"])) {
        $title = $_GET["title"];
    }
    if (isset($_GET["image"])) {
        $image = $_GET["image"];
    }
    
    if (isset($_GET["overview"])) {
        $overview = $_GET["overview"];
    }
    if (isset($_GET["genre"])) {
        $genre = $_GET["genre"];
    }
    if (isset($_GET["director"])) {
        $director = $_GET["director"];
    }
    if (isset($_GET["date"])) {
        $date = $_GET["date"];
    }
    if (isset($_GET["cast"])) {
        $cast = $_GET["cast"];
    }*/
    
    
    if (isset($_GET["fam1"])) {
        $fam1 = $_GET["fam1"];
    }
    if (isset($_GET["fam2"])) {
        $fam2 = $_GET["fam2"];
    }
    if (isset($_GET["conf"])) {
        $conf = $_GET["conf"];
    }
    
    $_SESSION[$SURVEYLINK]['log']->lwrite("survey","user\t".session_id().
        "\tsim\t".$sim.
        "\tpair\t".$pair.
       /* "\ttitle\t".$title.
        "\timage\t".$image.
        "\toverview\t".$overview.
        "\tgenre\t".$genre.
        "\tdirector\t".$director.
        "\tdate\t".$date.
        "\tcast\t".$cast.*/
        "\tfam1\t".$fam1.
        "\tfam2\t".$fam2.
        "\tconf\t".$conf.
        "\trandom\t".$_SESSION[$SURVEYLINK]['random'].
        "\tstep\t".(intval($_GET["step"])-1)
    );
    $_SESSION[$SURVEYLINK]['log']->lclose(); 
    require("demo.php");
    
} else if ($next_step == "finish") {

    /*$title ="NA";
    $image ="NA";
    $ingredients = "NA";
    $directions = "NA";*/
    //$occupation = "NA";
    $age = "NA";
    $gender = "NA";
    
    $newsws = "NA";
    
    $days_news = "NA";
    
    
    $title = "NA";
    $image = "NA";

    $text = "NA";
    $subcategory = "NA";
    $date = "NA";
    $sentiment = "NA";
    $n_author = "NA";
    $author_bios = "NA";

    
    /*if (isset($_GET["title"])) {
        $title = $_GET["title"];
    }
    if (isset($_GET["image"])) {
        $image = $_GET["image"];
    }
    if (isset($_GET["ingredients"])) {
        $ingredients = $_GET["ingredients"];
    }
    if (isset($_GET["directions"])) {
        $directions = $_GET["directions"];
    }*/
   /* if (isset($_GET["occupation"])) {
        $occupation = test_input($_GET["occupation"]);
    }*/
    if (isset($_GET["age"])) {
        $age = $_GET["age"];
    }
    if (isset($_GET["gender"])) {
        $gender = $_GET["gender"];
    }
    if (isset($_GET["newsws"])) {
        $newsws = $_GET["newsws"];
    }
    if (isset($_GET["days_news"])) {
        $days_news = $_GET["days_news"];
    }
    
    if (isset($_GET["title"])) {
       $title = $_GET["title"];
   }
   if (isset($_GET["image"])) {
       $image = $_GET["image"];
   }

   if (isset($_GET["text"])) {
       $text = $_GET["text"];
   }
   if (isset($_GET["subcategory"])) {
       $subcategory = $_GET["subcategory"];
   }
   if (isset($_GET["date"])) {
       $date = $_GET["date"];
   }
   if (isset($_GET["sentiment"])) {
       $sentiment = $_GET["sentiment"];
   }
   if (isset($_GET["n_author"])) {
    $n_author = $_GET["n_author"];
   }
   if (isset($_GET["author_bios"])) {
    $author_bios = $_GET["author_bios"];
   }


$_SESSION[$SURVEYLINK]['log']->lwrite("finish","user\t".session_id().
        /*"\ttitle\t".$title.
        "\timage\t".$image.
        "\tingredients\t".$ingredients.
        "\tdirections\t".$directions.*/
       // "\toccupation\t".$occupation.
        "\tage\t".$age.
        "\tgender\t".$gender.
        "\tnewsws\t".$newsws.
        "\tdays_news\t".$days_news.
        "\tsubcategory\t".$subcategory.
        "\ttitle\t".$title.
        "\timage\t".$image.
        "\tn_author\t".$n_author.
        "\tdate\t".$date.
        "\ttext\t".$text.
        "\tsentiment\t".$sentiment.
        "\tauthor_biography\t".$author_bios
    );


   // $_SESSION[$SURVEYLINK]['log']->lwrite("finish","User:\t".session_id());
$_SESSION[$SURVEYLINK]['log']->lclose();
require("finish.php");

} else {

    /*if ((($obj->counter-1)/$COUNTER) >= $MAX_HITS-1) {
        
       // unset($_SESSION[$SURVEYLINK]['pairs']);
      //  unset($_SESSION[$SURVEYLINK]['data']);
       // unset($_SESSION[$SURVEYLINK]['step']);
       
        $_SESSION[$SURVEYLINK]['log']->lwrite("closed","user\t".session_id());
        $_SESSION[$SURVEYLINK]['log']->lclose();
        
        require("start2.php");
       
    } else {*/

        $_SESSION[$SURVEYLINK]['log']->lwrite("start","user\t".session_id());
        $_SESSION[$SURVEYLINK]['log']->lclose();
        
    //    unset($_SESSION[$SURVEYLINK]['pairs']);
    //    unset($_SESSION[$SURVEYLINK]['data']);
   //     unset($_SESSION[$SURVEYLINK]['step']);
        
        require("start.php");
    //}
    }
} else {
    require("notallowed.php");
}

?>


</div>








</body>

</html>
