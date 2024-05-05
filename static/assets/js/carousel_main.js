// const imgs = document.getElementById("carousel_main_id");
// const leftBtn = document.getElementById("carousel_arrowleft_id");
// const rightBtn = document.getElementById("carousel_arrowright_id");

// const img = document.querySelectorAll("#carousel_main_id one_card");

// let idx = 0;

// let interval = setInterval(run, 2000);

// function run() {
//   idx++;

//   changeImg();
// }

// function changeImg() {
//   if (idx > img.length - 1) {
//     idx = 0;
//   } else if (idx < 0) {
//     idx = img.length - 1;
//   }

//   imgs.style.transform = `translateX(${-idx * 500}px)`;
// }

// function resetInterval() {
//   clearInterval(interval);
//   interval = setInterval(run, 2000);
// }

// rightBtn.addEventListener("click", () => {
//   idx++;

//   changeImg();
//   resetInterval();
// });

// leftBtn.addEventListener("click", () => {
//   idx--;
//   changeImg();
//   resetInterval();
// });
