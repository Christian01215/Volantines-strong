/*
 * Volantines Strong — carrito, checkout y drawer.
 * El carrito vive en base de datos; este archivo sólo consume la API JSON.
 */
(function () {
  'use strict';

  var NS = window.StrongStore || window;
  var URLS = window.STRONG_CART_URLS || {
    list: '/cart/api/',
    add: '/cart/api/agregar/',
    update: '/cart/api/actualizar/',
    remove: '/cart/api/quitar/',
    clear: '/cart/api/vaciar/'
  };

  var items = [];
  var count = 0;
  var total = 0;

  var drawer = NS.byId('cart-drawer');
  var container = NS.byId('cart-items-container');
  var badge = NS.byId('cart-badge');
  var totalLabel = NS.byId('cart-total');
  var itemsStep = NS.byId('cart-items-step');
  var footer = NS.byId('cart-footer');
  var form = NS.byId('checkout-form');

  function csrfToken() {
    var input = document.querySelector('[name="csrfmiddlewaretoken"]');
    if (input) return input.value;
    var match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
  }

  function post(url, data) {
    var body = new FormData();
    Object.keys(data || {}).forEach(function (key) {
      body.append(key, data[key]);
    });
    return fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'X-CSRFToken': csrfToken(),
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: body
    }).then(function (response) {
      return response.json().then(function (payload) {
        if (!response.ok || payload.ok === false) {
          throw new Error(payload.message || 'No se pudo completar la acción.');
        }
        return payload;
      });
    });
  }

  function apply(payload) {
    items = payload.items || [];
    count = payload.count || 0;
    total = payload.total || 0;
    render();
  }

  function refresh() {
    return fetch(URLS.list, { credentials: 'same-origin' })
      .then(function (response) { return response.json(); })
      .then(apply);
  }

  function render() {
    if (badge) badge.textContent = String(count);
    if (totalLabel) totalLabel.textContent = NS.formatCLP(total);
    if (!container) return;

    if (!items.length) {
      container.innerHTML = '<p class="text-sm text-slate-500">Tu carrito está vacío.</p>';
      return;
    }

    container.innerHTML = items.map(function (item) {
      var image = item.image
        ? '<img src="' + item.image + '" alt="' + item.name +
          '" class="w-16 h-16 object-contain rounded-lg bg-slate-50">'
        : '<span class="w-16 h-16 grid place-items-center rounded-lg bg-slate-100 ' +
          'text-slate-900 font-black italic">S</span>';

      var design = item.design_url
        ? '<a class="text-[10px] text-sky-700 underline block mt-1" href="' +
          item.design_url + '" target="_blank" rel="noopener">Ver diseño</a>'
        : '';

      return '' +
        '<div class="flex gap-3 items-center border-b border-slate-100 pb-3">' +
          image +
          '<div class="flex-1 min-w-0">' +
            '<p class="text-xs font-bold text-slate-900 truncate">' + item.name + '</p>' +
            '<p class="text-[11px] text-slate-500">' + item.category + '</p>' + design +
            '<div class="flex items-center gap-2 mt-1">' +
              '<button type="button" data-cart-action="minus" data-product-id="' + item.id +
                '" class="w-6 h-6 rounded border border-slate-300 text-slate-700 text-xs">−</button>' +
              '<span class="text-xs font-bold text-slate-900">' + item.quantity + '</span>' +
              '<button type="button" data-cart-action="plus" data-product-id="' + item.id +
                '" class="w-6 h-6 rounded border border-slate-300 text-slate-700 text-xs">+</button>' +
              '<button type="button" data-cart-action="remove" data-product-id="' + item.id +
                '" class="text-[10px] text-red-600 hover:underline ml-2">Quitar</button>' +
            '</div>' +
          '</div>' +
          '<span class="text-xs font-black text-slate-900">' +
            NS.formatCLP(item.line_total) +
          '</span>' +
        '</div>';
    }).join('');
  }

  function openDrawer() {
    if (!drawer) return;
    drawer.classList.remove('hidden');
    refresh();
  }

  function closeDrawer() {
    if (!drawer) return;
    drawer.classList.add('hidden');
  }

  function showCheckout() {
    if (!items.length) return;
    if (itemsStep) itemsStep.classList.add('hidden');
    if (footer) footer.classList.add('hidden');
    if (form) form.classList.remove('hidden');
  }

  function showCart() {
    if (form) form.classList.add('hidden');
    if (itemsStep) itemsStep.classList.remove('hidden');
    if (footer) footer.classList.remove('hidden');
  }

  function changeQuantity(productId, delta) {
    var item = items.filter(function (entry) {
      return String(entry.id) === String(productId);
    })[0];
    if (!item) return;
    post(URLS.update, { product_id: productId, quantity: item.quantity + delta })
      .then(apply)
      .catch(function (error) { window.alert(error.message); refresh(); });
  }

  window.StrongCart = {
    add: function (product, design) {
      if (!product || Number(product.stock) <= 0) return Promise.resolve(null);
      return post(URLS.add, {
        product_id: product.id,
        quantity: 1,
        design_url: (design && design.url) || '',
        design_name: (design && design.name) || ''
      }).then(function (payload) {
        apply(payload);
        showCart();
        openDrawer();
        return payload;
      }).catch(function (error) {
        window.alert(error.message);
        return null;
      });
    },
    items: function () { return items.slice(); },
    clear: function () {
      return post(URLS.clear, {}).then(function (payload) { apply(payload); });
    }
  };

  var openBtn = NS.byId('open-cart-btn');
  if (openBtn) openBtn.addEventListener('click', openDrawer);
  var closeBtn = NS.byId('close-cart-btn');
  if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
  var backdrop = NS.byId('cart-backdrop');
  if (backdrop) backdrop.addEventListener('click', closeDrawer);
  var checkoutBtn = NS.byId('proceed-checkout-btn');
  if (checkoutBtn) checkoutBtn.addEventListener('click', showCheckout);
  var backBtn = NS.byId('back-to-cart-btn');
  if (backBtn) backBtn.addEventListener('click', showCart);

  if (container) {
    container.addEventListener('click', function (event) {
      var button = event.target.closest('[data-cart-action]');
      if (!button) return;
      var productId = button.dataset.productId;
      if (button.dataset.cartAction === 'plus') changeQuantity(productId, 1);
      if (button.dataset.cartAction === 'minus') changeQuantity(productId, -1);
      if (button.dataset.cartAction === 'remove') {
        post(URLS.remove, { product_id: productId })
          .then(apply)
          .catch(function (error) { window.alert(error.message); refresh(); });
      }
    });
  }

  var dateInput = NS.byId('chk-date');
  if (dateInput) dateInput.min = new Date().toISOString().split('T')[0];

  if (form) {
    form.addEventListener('submit', async function (event) {
      event.preventDefault();

      var errorLabel = NS.byId('checkout-error');
      var submitBtn = NS.byId('submit-order-btn');

      if (errorLabel) errorLabel.classList.add('hidden');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Registrando pedido...';
      }

      try {
        var response = await fetch(form.action, {
          method: 'POST',
          body: new FormData(form),
          headers: {
            'X-CSRFToken': csrfToken(),
            'X-Requested-With': 'XMLHttpRequest'
          },
          credentials: 'same-origin'
        });
        var data = await response.json();

        if (!response.ok || !data.ok) {
          throw new Error(data.message || 'No se pudo registrar el pedido.');
        }

        if (container) {
          container.innerHTML = '' +
            '<div class="text-center py-8">' +
              '<p class="text-xs font-bold uppercase text-red-600">Pedido registrado</p>' +
              '<h4 class="text-2xl font-black text-slate-900 mt-2">' + data.code + '</h4>' +
              '<p class="text-xs text-slate-500 mt-2">' + data.message + '</p>' +
              '<a class="text-xs text-sky-700 underline block mt-3" href="' +
                URLS.success.replace('CODIGO', data.code) + '">Ver comprobante de retiro</a>' +
            '</div>';
        }

        if (itemsStep) itemsStep.classList.remove('hidden');
        if (footer) footer.classList.add('hidden');
        if (form) form.classList.add('hidden');
        window.StrongCart.clear();
      } catch (error) {
        if (errorLabel) {
          errorLabel.textContent = error.message;
          errorLabel.classList.remove('hidden');
        }
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Registrar pedido (pago pendiente)';
        }
      }
    });
  }

  refresh();
})();
