function fetchContacts() {
 /* var jsonString = '[{"name": "Dummy Student", "email": "stud1@test.quizer.info", "course": "Computer Science"}';
  jsonString += ',{"name": "Dummy Mwanfunzi", "email": "stud2@test.quizer.info", "course": "Computer Science"}';
  jsonString += ',{"name": "Dummy Mwanafunzi", "email": "stud3@test.quizer.info", "course": "Computer Science"}]';*/
  
  var response = UrlFetchApp.fetch("http://quizer-gapp.appspot.com/json");
  var jsonString = response.getContentText();
//  Logger.log(jsonString);
 // Logger.log(response.getResponseCode());
 // Logger.log(response.getAllHeaders());
  Logger.log(jsonString);
  return jsonString;
}

function addContacts(jsonString){
  var student = Utilities.jsonParse(jsonString);
  var qa_group = ContactsApp.getContactGroup('QuizerApp');
  if(!qa_group){
    qa_group = ContactsApp.createContactGroup('QuizerApp');
  }
  for (var i in student){
    //check if email already added, not sure whether it is costly 
    //if(!ContactsApp.getContact(student[i].email)){ -- was costly
    
    //option two: after successfully adding, send back json with emails that have been added, not to be fetched again===> later
    var c = ContactsApp.createContact(student[i].name,' ', student[i].email);
    //add the contact to the QuizerApp group
    qa_group.addContact(c);
  }
  
  //give report of the number of contacts added
  i++;
  Logger.log(i+" contacts added");
  return i;
}

function doGet(e){
  //var output = ContentService.createTextOutput();
  //output.setContent(testContactsAPI());
  //return output;
  var added = addContacts(fetchContacts());
  if(added>0){
    return HtmlService.createTemplateFromFile('output').evaluate();
  }else{
    //dispaly page showing that contacts have not been added
  }
}