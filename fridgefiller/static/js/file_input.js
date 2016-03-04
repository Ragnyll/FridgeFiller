$(function() {
  var App = {
    init: function() {
      App.attachListeners();
    },
    attachListeners: function() {
      var self = this;

      $(".fa-barcode button").on("click", function(e) {
        var input = {};
        $(this).find("input").click();
        input = $(this).find("input").val();
        if (input.files && input.files.length) {
          App.decode(URL.createObjectURL(input.files[0]));
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
      $(". input[type=file]").off("change");
      $(".controls .reader-config-group").off("change", "input, select");
      $(".controls button").off("click");
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

      console.log(JSON.stringify(self.state));
      App.detachListeners();
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
    }
  };
  
  App.init();

  Quagga.onDetected(function(result) {
    var code = result.codeResult.code,
        $node,
        canvas = Quagga.canvas.dom.image;

    $("")
  });
});
