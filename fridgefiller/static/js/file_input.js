$(function() {
  var App = {
    init: function() {
      App.attachListeners();
    },
    attachListeners: function() {
      var self = this;

      // Click file selection input field and clear any previous result classes
      $(".fa-barcode").on("click", function(e) {
        var input = $(this).find('input[type=file]')[0],
            value = $(input).context.files;
        $(input).context.click();
        $(this).removeClass('btn-danger btn-success').addClass('btn-warning');
      });

      // Call Quagga decode function using selected file.
      $('.scan-barcode-input').change(function(e) {
        App.ids = $(this).attr('id').split(" ");
        if (e.target.files && e.target.files.length) {
          App.decode(URL.createObjectURL(e.target.files[0]));
        }
        $(this).val("");
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

      Quagga.decodeSingle(config, function(result) {
        if(!result || !result.codeResult) {
          $('#scan-barcode-button-' + App.ids[0]).removeClass("btn-warning", 1000).addClass("btn-danger");
          // Flashes on and off, not sure if especially useful
          // setTimeout(function() {
            // $('#scan-barcode-button-' + App.ids[0]).removeClass("btn-danger").addClass("btn-warning");
          // }, 1000);
        }
      });
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
        $('#scan-barcode-button-' + App.ids[0]).removeClass("btn-warning", 1000).addClass("btn-success");
        var node= $('#scan-barcode-button-' + App.ids[0]).siblings("#new-item-name");
        $(node).val(data.item_name);
        node = $('#scan-barcode-button-' + App.ids[0]).siblings("#new-item-desc");
        $(node).val(data.item_desc);
        // Flashes on and off, not sure if especially useful
        // setTimeout(function() {
          // $('#scan-barcode-button-' + App.ids[0]).removeClass("btn-success").addClass("btn-warning");
        // }, 1000);
      })
      .fail(function(data) {
        $('#scan-barcode-button-' + App.ids[0]).removeClass("btn-warning", 1000).addClass("btn-danger");
        // Flashes on and off, not sure if especially useful
        // setTimeout(function() {
          // $('#scan-barcode-button-' + App.ids[0]).removeClass("btn-danger").addClass("btn-warning");
        // }, 1000);
      });
  });
});
