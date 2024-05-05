$(document).ready(function () {
  // Product Filter Start
  $(".filter-checkbox").on("click", function () {
    var _filterObj = {};
    $(".filter-checkbox").each(function (index, ele) {
      var _filterVal = $(this).val();
      var _filterKey = $(this).data("filter");
      _filterObj[_filterKey] = Array.from(
        document.querySelectorAll(
          "input[data-filter=" + _filterKey + "]:checked"
        )
      ).map(function (el) {
        return el.value;
      });
    });
    var attr_id = $(this).attr("attr_id");
    var action_url = $(this).attr("action_url");
    // Run Ajax
    $.ajax({
      url: action_url,
      data: attr_id ,
      dataType: "json",
      beforeSend: function () {
        $(".ajaxLoader").show();
      },
      success: function (res) {
        console.log(res);
        $("#filteredProducts").html(res.data);
      },
    });
  });
  // End
});
