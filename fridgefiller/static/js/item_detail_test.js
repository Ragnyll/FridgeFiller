$(function() {
  var test = {
    init: function() {
      test.attachListeners();
    },
    attachListeners: function() {
      var self = this;

      $(".controls1 button").on("click", function(e) {
        var input = document.querySelector(".controls1 input[type=text]"),
            $node;
        $.get("walapi1", {'item-name':input.value})
          .done(function(data) {
            $node = $('<p><button>X</button></p>');
            $node.prepend(data.items[0].name);
            $node.find("button").on("click", function(e) {
              $(this).parent().remove();
            });
            $("div.test#hoho").prepend($node);
          })
          .fail(function(data) {
            alert("Borked");
          });
      });

      
      $(".controls2 button").on("click", function(e) {
        var input = document.querySelector(".controls2 input[type=text]"),
            $node;
        $.get("walapi2", {'upc': input.value})
          .done(function(data) {
            $node = $('<p><button>X</button></p>');
            $node.prepend(data.items[0].name);
            $node.find("button").on("click", function(e) {
              $(this).parent().remove();
            });
            $("div.test#haha").prepend($node);
          })
          .fail(function(data) {
            alert("Borked");
          });
      });
    }
  };

  test.init();
});
