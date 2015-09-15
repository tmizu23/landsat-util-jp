thumbnail = "thumbnail"

function myselect(e,f){
  arr = f.split("/");
  pr = arr[arr.length-1].substr(3,6);
  var elms = document.getElementsByClassName("pr" + pr);
  if(!document.chbox.elements[0].checked){
     for(var i=0;i<elms.length;i++){
       elms[i].style.border="none";
     }
  }
  var img = document.getElementById("pr"+pr);
  img.src = f;
  e.style.border = "solid 1px black";
  e.style.borderColor ="red";
}

function makelist(){
  file_url = location.href
  file_url = file_url.substring(file_url.lastIndexOf("/")+1,file_url.length)
  file_url = file_url.substring(0,file_url.indexOf("."));

  if(!document.chbox.elements[0].checked) selectedhtml(file_url)

  var list="";
  var elms = document.getElementsByTagName("img")
  for(var i=0;i<elms.length;i++){
     if(elms[i].style.border!="" && elms[i].style.border!="none"){
        list = list + elms[i].src.substring(elms[i].src.lastIndexOf("/")+1, elms[i].src.length).replace(".jpg","") + "\n"
     }
  }
  /*
  for(var p=104;p<=116;p++){
    for(var r=28;r<=43;r++){
     var img = document.getElementById("pr" + p +"0" + r);
     if(img!=null && img.src.indexOf(".jpg") != -1)
      list = list + img.src.substring(img.src.lastIndexOf("/")+1, img.src.length).replace(".jpg","") + "\n"
    }
  }
  */
  var blob = new Blob( [list], {type: "text/plain"} );
  var link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = file_url + ".txt";
  link.click();

}

function selectedhtml(file_url){
  var html="";
  html += '<table cellpadding="0" style="border: solid 1px #000000; border-collapse: collapse;font-size:xx-small">'
  html += '<tr><th style="border: solid 1px #000000;width:40px"></th>'
  for(var p=116;p>=104;p--){
    html += '<th style="border: solid 1px #000000;width:40px">' + p + '</th>'
  }
  html += '</tr>\n'
  for(var r=28;r<=43;r++){
    html += '<tr><th style="border: solid 1px #000000;">' + r + '</th>'
    for(var p=116;p>=104;p--){
      var img = document.getElementById("pr" + p +"0" + r);
      html += '<td><img src="' + img.src + '" width="300"></td>'
    }
    html += '</tr>\n'
  }
  html += '</table>'

  var blob = new Blob( [html], {type: "text/plain"} );
  var link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = file_url + "selected.html";
  link.click();
}

function importlist(){
  var elms = document.getElementsByTagName("table")//テーブル指定。あってる？
  for(var i=0;i<elms.length;i++){
    elms[i].style.border="none";
  }
  var obj1 = document.getElementById("listfile");
  obj1.addEventListener("change",function(evt){
     var file = evt.target.files;
     var reader = new FileReader();
     reader.readAsText(file[0]);
     reader.onload = function(ev){
        lines = reader.result.split('\n');
        for ( var i = 0; i < lines.length; i++ ) {
           if ( lines[i] == '' ) {
              continue;
           }
           var img = document.getElementById("pr" +lines[i].substr(3,6));
           img.src = thumbnail + "/" + lines[i] + ".jpg";
           var e = document.getElementById(lines[i]);//?? idをhtmlに作る
           e.style.border = "solid 1px black";
           e.style.borderColor ="red";
        }
     }
  },false);
}
