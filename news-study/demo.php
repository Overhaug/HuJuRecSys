
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
  left:9.5%;
  display:block;
  background-color:#858C93;
  height:4px;
  width:74%;
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

</style>

<script language="javascript" type="text/javascript">

  function checkedRadioBtn(sGroupName) {   
    var group = document.getElementsByName(sGroupName);
    console.log(group);
    for (var i = 0; i < group.length; i++) {
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
            if(checkedRadioBtn("n_author") &&
             checkedRadioBtn("age") &&
             checkedRadioBtn("gender") &&
             checkedRadioBtn("newsws") &&
             checkedRadioBtn("title") &&
             checkedRadioBtn("image") &&
             checkedRadioBtn("text") &&
             checkedRadioBtn("author_bios") &&
             checkedRadioBtn("subcategory") &&
             checkedRadioBtn("sentiment") &&
             checkedRadioBtn("date")) {
              document.demo_form.action = "index.php";
              document.demo_form.submit();
          } else {
            alert('Please checked that you have responded to all of the questions!');
          }
        }
      </script>



      <div class="jumbotron">

        <form id="demo_form" name="demo_form" action="index.php" method="GET">


          <h2>To finish, please complete the questionnaire below!</h2>
          <hr>


          <h5>What is your age?</h5>
          <input type="radio" name="age" value="<18"> Less than 18<br />
          <input type="radio" name="age" value="18-24"> 18-24<br />
          <input type="radio" name="age" value="25-34"> 25-34<br />
          <input type="radio" name="age" value="35-44"> 35-44<br />
          <input type="radio" name="age" value="45-54"> 45-54<br />
          <input type="radio" name="age" value=">55"> 55 and over<br />
          <input type="radio" name="age" value="NA"> I'd rather not say<br />
          <br />

          <h5>What is your gender?</h5>
          <input name="gender" type="radio" value="Male"> Male<br />
          <input name="gender" type="radio" value="Female"> Female<br />
          <input name="gender" type="radio" value="Other"> Other<br />
          <br />

          <h5>Which of the following statements best describes your use of online newspapers (e.g. The Washington Post, The New York Times, etc)?</h5>

          <input name="newsws" type="radio" value="1"> I use them almost on a daily basis <br />
          <input name="newsws" type="radio" value="2"> I use them at least once per week <br />
          <input name="newsws" type="radio" value="3"> I use them at least once per month <br />
          <input name="newsws" type="radio" value="4"> I use them at least once every three months <br />
          <input name="newsws" type="radio" value="5"> I hardly use them at all <br />
          <br />
          <h5>Over the course of a week, how many days do you access online newspapers?</h5>
          <select name="days_news">
            <option value="0">0</option>
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
            <option value="6">6</option>
            <option value="7">7</option>
          </select><br />
          <hr />

          <h5>To what extent do you agree with the following statements:</h5>

          I looked at the <b>subcategory</b> to estimate the similarity between the news:
          <ul class='likert'>
            <li>
              <input type="radio" name="subcategory" value="1">
              <label>1 <br>(Totally Disagree)</label>
            </li>
            <li>
              <input type="radio" name="subcategory" value="2">
              <label>2</label>
            </li>
            <li>
              <input type="radio" name="subcategory" value="3">
              <label>3</label>
            </li>
            <li>
              <input type="radio" name="subcategory" value="4">
              <label>4</label>
            </li>
            <li>
              <input type="radio" name="subcategory" value="5">
              <label>5 <br>(Totally Agree)</label>
            </li>
          </ul>
          <br>

          I looked at the <b>news title</b> to estimate the similarity between the articles:
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
          <br>

          I looked at the <b>news image</b> to estimate the similarity between the news:
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
          <br>

          I looked at the <b>author(s)</b> to estimate the similarity between the news:
          <ul class='likert'>
            <li>
              <input type="radio" name="n_author" value="1">
              <label>1 <br>(Totally Disagree)</label>
            </li>
            <li>
              <input type="radio" name="n_author" value="2">
              <label>2</label>
            </li>
            <li>
              <input type="radio" name="n_author" value="3">
              <label>3</label>
            </li>
            <li>
              <input type="radio" name="n_author" value="4">
              <label>4</label>
            </li>
            <li>
              <input type="radio" name="n_author" value="5">
              <label>5 <br>(Totally Agree)</label>
            </li>
          </ul>
          <br>

          I looked at the <b>date of publication</b> to estimate the similarity between the news:
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

          I looked at the <b>article body text</b> to estimate the similarity between the news:
          <ul class='likert'>
            <li>
              <input type="radio" name="text" value="1">
              <label>1 <br>(Totally Disagree)</label>
            </li>
            <li>
              <input type="radio" name="text" value="2">
              <label>2</label>
            </li>
            <li>
              <input type="radio" name="text" value="3">
              <label>3</label>
            </li>
            <li>
              <input type="radio" name="text" value="4">
              <label>4</label>
            </li>
            <li>
              <input type="radio" name="text" value="5">
              <label>5 <br>(Totally Agree)</label>
            </li>
          </ul>
          <br>

          I reviewed the <b>sentiment of the article body text</b> to estimate the similarity between the news:
          <ul class='likert'>
            <li>
              <input type="radio" name="sentiment" value="1">
              <label>1 <br>(Totally Disagree)</label>
            </li>
            <li>
              <input type="radio" name="sentiment" value="2">
              <label>2</label>
            </li>
            <li>
              <input type="radio" name="sentiment" value="3">
              <label>3</label>
            </li>
            <li>
              <input type="radio" name="sentiment" value="4">
              <label>4</label>
            </li>
            <li>
              <input type="radio" name="sentiment" value="5">
              <label>5 <br>(Totally Agree)</label>
            </li>
          </ul>
          <br>

          I looked at the <b>author biographies</b> to estimate the similarity between the news:
          <ul class='likert'>
            <li>
              <input type="radio" name="author_bios" value="1">
              <label>1 <br>(Totally Disagree)</label>
            </li>
            <li>
              <input type="radio" name="author_bios" value="2">
              <label>2</label>
            </li>
            <li>
              <input type="radio" name="author_bios" value="3">
              <label>3</label>
            </li>
            <li>
              <input type="radio" name="author_bios" value="4">
              <label>4</label>
            </li>
            <li>
              <input type="radio" name="author_bios" value="5">
              <label>5 <br>(Totally Agree)</label>
            </li>
          </ul>
          <br>

          <hr>


          <br />

          <div align="center">
            <input type="hidden" id="user_id" name="user_id" value="<?php echo session_id() ?>" />
            <input type="hidden" name="next_step" value="finish" />
            <input type="hidden" name="survey_id" value="<?php echo $SID ?>" />
            <button type="button" class="btn btn-lg btn-success" onclick="javascript:checkForm();">Finish Survey!</button>
          </div>
        </form>

      </div>
