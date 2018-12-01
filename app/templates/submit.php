<?php
if(isset($_POST['submit'])){
    $nameArr = $_POST['name'];
    $emailArr = $_POST['email'];
    if(!empty($nameArr)){
        for($i = 0; $i < count($nameArr); $i++){
            if(!empty($nameArr[$i])){
                $name = $nameArr[$i];
                $email = $emailArr[$i];

                //database insert query goes here
            }
        }
    }
}
?>