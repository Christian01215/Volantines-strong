/*
 * Volantines Strong — panel de administración.
 * Reconstruido para conservar la etiqueta <script src="js/admin.js"> original.
 * El dashboard es server-rendered: este archivo sólo gestiona las acciones.
 */
(function () {
  'use strict';

  function csrfToken() {
    var input = document.querySelector('[name="csrfmiddlewaretoken"]');
    return input ? input.value : '';
  }

  function parseJson(response) {
    var type = response.headers.get('content-type') || '';
    if (type.indexOf('application/json') === -1) {
      return response.text().then(function (text) {
        var detail = text.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 120);
        throw new Error(
          'Error del servidor (' + response.status + '). ' +
          (detail || 'Revisa los logs de Vercel.')
        );
      });
    }
    return response.json();
  }

  function post(url, body) {
    return fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'X-CSRFToken': csrfToken(),
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: body || new FormData()
    }).then(function (response) {
      return parseJson(response).then(function (data) {
        if (!response.ok || data.ok === false) {
          throw new Error(data.message || 'No se pudo completar la acción.');
        }
        return data;
      });
    });
  }

  // El botón "Actualizar pedidos" de admin.html recarga el server-rendered.
  window.loadAdminOrders = function () {
    window.location.reload();
  };

  // El reporte se genera en el servidor para incluir TODOS los pedidos
  // y el resumen de ganancias mensuales.
  var exportBtn = document.getElementById('export-orders-btn');
  if (exportBtn) {
    exportBtn.addEventListener('click', function () {
      window.location.href = exportBtn.dataset.url || '/admin-panel/pedidos/exportar/';
    });
  }

  // Cambio de estado desde el selector de la tabla.
  document.addEventListener('change', function (event) {
    var select = event.target;
    if (!select.matches('select[data-order-id][data-url]')) return;

    var body = new FormData();
    body.append('status', select.value);
    post(select.dataset.url, body)
      .then(function (data) {
        if (data && data.warning) window.alert(data.warning);
        window.location.reload();
      })
      .catch(function (error) {
        window.alert(error.message);
        window.location.reload();
      });
  });

  // Acciones de filas: editar producto, eliminar, notificar.
  document.addEventListener('click', function (event) {
    var button = event.target.closest('[data-action], [data-url]');
    if (!button || button.matches('select[data-order-id]')) return;
    if (button.id === 'export-orders-btn') return;

    var action = button.dataset.action;

    if (action === 'edit-product') {
      var row = button.closest('tr');
      if (!row) return;

      var values = {
        prod_id: row.dataset.id,
        prod_name: row.dataset.name,
        prod_category: row.dataset.category,
        prod_price: row.dataset.price,
        prod_cost: row.dataset.cost || '0',
        prod_stock: row.dataset.stock,
        prod_specs: row.dataset.specs,
        prod_desc: row.dataset.description
      };
      Object.keys(values).forEach(function (key) {
        var field = document.querySelector('[name="' + key + '"]');
        if (field) field.value = values[key] || '';
      });

      var title = document.getElementById('form-title');
      if (title) title.textContent = 'Editar producto';
      var saveBtn = document.getElementById('save-prod-btn');
      if (saveBtn) saveBtn.textContent = 'Actualizar producto ↗';
      var cancelBtn = document.getElementById('cancel-edit-btn');
      if (cancelBtn) cancelBtn.classList.remove('hidden');

      document.getElementById('product-form').scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }

    var row = button.closest('tr');
    var url = button.dataset.url;
    if (!url && row) {
      if (action === 'delete-product') url = row.dataset.deleteUrl;
      if (action === 'restore-product') url = row.dataset.restoreUrl;
      if (action === 'purge-product') url = row.dataset.purgeUrl;
    }
    if (!url) return;

    if (action === 'delete-product') {
      if (!window.confirm('¿Desactivar este producto? No se borrará del historial de pedidos.')) return;
    }
    if (action === 'restore-product') {
      if (!window.confirm('¿Reactivar este producto?')) return;
    }
    if (action === 'purge-product') {
      if (!window.confirm('¿Eliminar definitivamente este producto? Esta acción no se puede deshacer. Sólo se permite si no aparece en pedidos.')) return;
    }
    if (action === 'delete-order') {
      if (!window.confirm('¿Eliminar este pedido?')) return;
    }

    post(url)
      .then(function (data) {
        if (data && data.message) window.alert(data.message);
        window.location.reload();
      })
      .catch(function (error) { window.alert(error.message); });
  });

  var cancelBtn = document.getElementById('cancel-edit-btn');
  if (cancelBtn) {
    cancelBtn.addEventListener('click', function () {
      window.location.href = window.location.pathname;
    });
  }

  // Preview de la galería seleccionada en el formulario de producto.
  var galleryInput = document.getElementById('prod-gallery-files');
  var galleryPreview = document.getElementById('product-gallery-preview');
  if (galleryInput && galleryPreview) {
    galleryInput.addEventListener('change', function () {
      galleryPreview.innerHTML = '';
      Array.prototype.slice.call(galleryInput.files).slice(0, 4).forEach(function (file) {
        var item = document.createElement('div');
        item.className = 'gallery-preview-item';
        var img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.alt = file.name;
        item.appendChild(img);
        galleryPreview.appendChild(item);
      });
    });
  }
})();
