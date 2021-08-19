var avatar = document.getElementById("avatar")

var avatarModal = document.getElementById("avatarModal");

var span = document.getElementsByClassName("close")[1];

var btn = document.getElementById("myBtn");

var modal = document.getElementById("myModal");

var span2 = document.getElementsByClassName("close")[0];



btn.onclick = function () {
// When the user clicks the button, open the modal
  modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}



avatar.onclick = function () {
  avatarModal.style.display = "block"
}

span2.onclick = function() {
  avatarModal.style.display = "none";
}

window.onclick = function(event) {
  if (event.target == avatarModal) {
    avatarModal.style.display = "none";
  }
}
