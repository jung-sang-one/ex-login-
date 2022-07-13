const $review_name = document.querySelector(".review_name");
const $ckindx = document.querySelector(".ckindex");
const clientData = $ckindx.dataset.idx;
console.log(clientData);

let rows;
let uniteCheck;
$.ajax({
  type: "get",
  dataType: "json",
  url: "https://www.thecocktaildb.com/api/json/v1/1/filter.php?g=Cocktail_glass",
  data: {},
  success: function (result) {
    rows = result.drinks;

    rows[0].index = 0;
    for (let i = 0; i < rows.length; i++) {
      rows[i].index = rows[0].index + i;
      let ckname = rows[i].strDrink;
      let img = rows[i].strDrinkThumb;
      let html_temp = `<div class="card">
                                        <a href="/review/${rows[i].idDrink}">
                                        <img src="${img}/preview" class="card-img-top">
                                        </a>
                                        <div class="card-body">
                                          <h5 class="card-title">${ckname}</h5>
                                        </div>
                                        </div>`;
      let review_temp = `  <div class='bottomBox'>
                                        <input type="text" class="commentBox${i}" placeholder="댓글을 입력하세요 !">
                                        <button class="inputBtn" onclick="save_comment(${i})">입력</button>
                                        <button class="spreadBtn${i}" onclick="spread(${i})" id="rightBtn${i}">보기</i></button>            
                                    </div>
                                    <ul class="commentList ${i}" id="commentList${i}">
                                    </ul>
                                  </div>`;
      $(".card-group").append(html_temp);
      if (`${ckname}` === $review_name.innerText) {
        $(".review-group").append(review_temp);
      }
    }
  },
}).then(() => {
  $.ajax({
    type: "get",
    url: "/cocktail",
    success: function (result) {
      console.log(rows);
      let commentrows = result["comment"];
      for (let i = 0; i < commentrows.length; i++) {
        let text = `<li>${commentrows[i]["nick"]} : ${commentrows[i]["comment"]}</li>`;
        for (let i = 0; i < rows.length; i++) {
          if (rows[i].idDrink == clientData) {
            uniteCheck = rows[i];
          }
        }
        if (parseInt(commentrows[i]["index"]) == uniteCheck.index) {
          $(".review-group").append(text);
        }
      }
    },
  });
});

function save_comment(index) {
  let comment = $(`.commentBox${index}`).val();
  let nick = $(".myNickName").text();
  if (comment === "") {
    alert("댓글을 입력해 주세요!");
    return;
  } else {
    $.ajax({
      type: "POST",
      url: "/cocktail",
      data: { comment_give: comment, index_give: index, nick_give: nick },
      success: function (response) {
        alert(response["msg"]);
        window.location.reload();
      },
    });
  }
}

function filter() {
  let search = document.getElementById("search").value.toLowerCase();
  // console.log(search);
  let list = document.getElementsByClassName("card");
  // console.log(list);
  for (let i = 0; i < list.length; i++) {
    let searchname = list[i];
    if (searchname.innerText.toLowerCase().includes(search)) {
      list[i].style.display = "block";
    } else {
      list[i].style.display = "none";
    }
  }
}
