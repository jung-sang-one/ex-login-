const $review_name = document.querySelector(".review_name");
$.ajax({
  type: "get",
  dataType: "json",
  url: "https://www.thecocktaildb.com/api/json/v1/1/filter.php?g=Cocktail_glass",
  data: {},
  success: function (result) {
    let rows = result.drinks;
    for (let i = 0; i < rows.length; i++) {
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
});

function save_comment(index) {
  let comment = $(`.commentBox${index}`).val();
  if (comment === "") {
    alert("댓글을 입력해 주세요!");
    return;
  } else {
    $.ajax({
      type: "POST",
      url: "/cocktail",
      data: { comment_give: comment, index_give: index },
      success: function (response) {
        alert(response["msg"]);
        window.location.reload();
      },
    });
  }
}

function spread(index) {
  $(`.${index}`).empty();
  $.ajax({
    type: "get",
    url: "/cocktail",
    success: function (result) {
      let rows = result["comment"];
      rows.forEach((item) => {
        let text = `<li>${item["comment"]}</li>`;
        if (item["index"] == index) {
          $(`.${index}`).append(text);
        }
      });
    },
  });
  const id = document.querySelector(`#rightBtn${index}`);
  if (id.className == `spreadBtn${index}`) {
    $(`.${index}`).show();
    id.setAttribute("class", `closeBtn${index}`);
  } else if (id.className == `closeBtn${index}`) {
    $(`.${index}`).hide();
    id.setAttribute("class", `spreadBtn${index}`);
  }
}
