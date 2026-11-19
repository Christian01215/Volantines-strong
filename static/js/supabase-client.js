/*
 * Volantines Strong — capa de datos / utilidades compartidas.
 *
 * refvisual/ no incluía archivos .js: el HTML original sólo referenciaba
 * js/supabase-client.js, js/store.js y js/cart.js. Este archivo reconstruye
 * esa primera capa para conservar la etiqueta <script> original y dar
 * soporte a la interactividad de la tienda sin alterar una sola clase
 * visual del diseño de referencia.
 */
(function () {
  'use strict';

  var NS = (window.StrongStore = window.StrongStore || {});

  NS.byId = function (id) {
    return document.getElementById(id);
  };

  NS.formatCLP = function (value) {
    var number = Number(value) || 0;
    return '$' + number.toLocaleString('es-CL');
  };

  NS.storage = {
    get: function (key, fallback) {
      try {
        var raw = window.localStorage.getItem(key);
        return raw ? JSON.parse(raw) : fallback;
      } catch (error) {
        return fallback;
      }
    },
    set: function (key, value) {
      try {
        window.localStorage.setItem(key, JSON.stringify(value));
      } catch (error) {
        /* almacenamiento no disponible: la sesión sigue siendo funcional */
      }
    },
    remove: function (key) {
      try {
        window.localStorage.removeItem(key);
      } catch (error) {
        /* no-op */
      }
    }
  };

  NS.config = {
    supabaseUrl: '',
    supabaseKey: '',
    isConfigured: function () {
      return Boolean(this.supabaseUrl && this.supabaseKey);
    }
  };

  document.dispatchEvent(new CustomEvent('strong:data-ready'));
})();
