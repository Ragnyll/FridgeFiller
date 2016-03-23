$(function() {
  var App = {
    init: function() {
      App.attachListeners();
    },
    attachListeners: function() {
      var self = this;

      $(".fa-barcode").on("click", function(e) {
        var input = $(this).find('input[type=file]')[0];
        input.click();
      });

      $('.scan-barcode-input').change(function(e) {
        App.ids = $(this).attr('id').split(" ");
        if (e.target.files && e.target.files.length) {
          App.decode(URL.createObjectURL(e.target.files[0]));
        }
      });
    },
    _accessByPath: function(obj, path, val) {
      var parts = path.split('.'),
          depth = parts.length,
          setter = (typeof val !== "undefined") ? true : false;

      return parts.reduce(function(o, key, i) {
        if (setter && (i + 1) === depth) {
          o[key] = val;
        }
        return key in o ? o[key] : {};
      }, obj);
    },
    _convertNameToState: function(name) {
      return name.replace("_", ".").split("-").reduce(function(result, value) {
        return result + value.charAt(0).toUpperCase() + value.substring(1);
      });
    },
    detachListeners: function() {
      $(".scan-barcode-input input[type=file]").off("change");
      $(".fa-barcode button").off("click");
    },
    decode: function(src) {
      var self = this,
          config = $.extend({}, self.state, {src: src});

      Quagga.decodeSingle(config, function(result) {});
    },
    setState: function(path, value) {
      var self = this;

      if (typeof self._accessByPath(self.inputMapper, path) === "function") {
        value = self._accessByPath(self.inputMapper, path)(value);
      }

      self._accessByPath(self.state, path, value);

      App.detachListeners();
      App.ids = {};
      App.init();
    },
    inputMapper: {},
    state: {
      inputStream: {
        size: 640,
        singleChannel: false,
      },
      locator: {
        patchSize: "large",
        halfSample: false
      },
      numOfWorkers: 1,
      decoder: {
        readers: ["upc_reader"]
      },
      locate: true,
      src: null
    },
    ids: {}
  };
  
  App.init();

  Quagga.onDetected(function(result) {
    var code = result.codeResult.code,
        $node;
    $.get("walapi2", {'upc': code})
      .done(function(data) {
        var well = $('#scan-barcode-button-' + App.ids[0] + '-' + App.ids[1]).parents().find(".item-well");
        $(well).find("div.col-md-4 h4").html(data.items[0].name);
      })
      .fail(function(data) {
        alert("Borked");
      });
  });
});
