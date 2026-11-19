/*
 * Volantines Strong — carrito, checkout y drawer.
 * Reconstruido para conservar la etiqueta <script src="js/cart.js"> original.
 */
(function () {
  'use strict';

  var NS = window.StrongStore || window;
  var KEY = 'volantines-strong-cart';
  var items = NS.storage ? NS.storage.get(KEY, []) : [];
  if (!Array.isArray(items)) items = [];

  var drawer = NS.byId('cart-drawer');
  var container = NS.byId('cart-items-container');
  var badge = NS.byId('cart-badge');
  var totalLabel = NS.byId('cart-total');
  var itemsStep = NS.byId('cart-items-step');
  var footer = NS.byId('cart-footer');
  var form = NS.byId('checkout-form');

  function save() {
    if (NS.storage) NS.storage.set(KEY, items);
  }

  function totalQuantity() {
    return items.reduce(function (sum, item) {
      return sum + (Number(item.quantity) || 0);
    }, 0);
  }

  function totalPrice() {
    return items.reduce(function (sum, item) {
      return sum + (Number(item.price) || 0) * (Number(item.quantity) || 0);
    }, 0);
  }

  function render() {
    if (badge) badge.textContent = String(totalQuantity());
    if (totalLabel) totalLabel.textContent = NS.formatCLP(totalPrice());

    if (!container) return;

    if (!items.length) {
      container.innerHTML =
        '<p class="text-sm text-slate-500">Tu carrito está vacío.</p>';
      return;
    }

    container.innerHTML = items.map(function (item, index) {
      var image = item.image
        ? '<img src="' + item.image + '" alt="' + item.name +
          '" class="w-16 h-16 object-contain rounded-lg bg-slate-50">'
        : '<span class="w-16 h-16 grid place-items-center rounded-lg bg-slate-100 ' +
          'text-slate-900 font-black italic">S</span>';

      return '' +
        '<div class="flex gap-3 items-center border-b border-slate-100 pb-3">' +
          image +
          '<div class="flex-1 min-w-0">' +
            '<p class="text-xs font-bold text-slate-900 truncate">' + item.name + '</p>' +
            '<p class="text-[11px] text-slate-500">' + item.category + '</p>' +
            '<div class="flex items-center gap-2 mt-1">' +
              '<button type="button" data-cart-action="minus" data-index="' + index +
                '" class="w-6 h-6 rounded border border-slate-300 text-slate-700 text-xs">−</button>' +
              '<span class="text-xs font-bold text-slate-900">' + item.quantity + '</span>' +
              '<button type="button" data-cart-action="plus" data-index="' + index +
                '" class="w-6 h-6 rounded border border-slate-300 text-slate-700 text-xs">+</button>' +
              '<button type="button" data-cart-action="remove" data-index="' + index +
                '" class="text-[10px] text-red-600 hover:underline ml-2">Quitar</button>' +
            '</div>' +
          '</div>' +
          '<span class="text-xs font-black text-slate-900">' +
            NS.formatCLP(item.price * item.quantity) +
          '</span>' +
        '</div>';
    }).join('');
  }

  function openDrawer() {
    if (!drawer) return;
    drawer.classList.remove('hidden');
    render();
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

  function updateQuantity(index, delta) {
    var item = items[index];
    if (!item) return;
    item.quantity += delta;
    if (item.quantity <= 0) items.splice(index, 1);
    save();
    render();
  }

  window.StrongCart = {
    add: function (product) {
      if (!product || Number(product.stock) <= 0) return;
      var found = items.filter(function (item) {
        return String(item.id) === String(product.id);
      })[0];
      if (found) {
        found.quantity += 1;
      } else {
        items.push({
          id: product.id,
          name: product.name,
          category: product.category,
          price: product.price,
          priceLabel: product.priceLabel,
          image: product.image,
          quantity: 1
        });
      }
      save();
      render();
      showCart();
      openDrawer();
    },
    items: function () {
      return items.slice();
    },
    clear: function () {
      items = [];
      save();
      render();
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
      var index = Number(button.dataset.index);
      if (button.dataset.cartAction === 'plus') updateQuantity(index, 1);
      if (button.dataset.cartAction === 'minus') updateQuantity(index, -1);
      if (button.dataset.cartAction === 'remove') {
        items.splice(index, 1);
        save();
        render();
      }
    });
  }

  document.querySelectorAll('input[name="delivery_type"]').forEach(function (input) {
    input.addEventListener('change', function () {
      var clickCollect = NS.byId('fields-click-collect');
      var delivery = NS.byId('fields-delivery');
      if (clickCollect) {
        clickCollect.classList.toggle('hidden', input.value !== 'click_collect');
      }
      if (delivery) {
        delivery.classList.toggle('hidden', input.value !== 'delivery');
      }
    });
  });

  var dateInput = NS.byId('chk-date');
  if (dateInput) dateInput.min = new Date().toISOString().split('T')[0];

  if (form) {
    form.addEventListener('submit', function (event) {
      event.preventDefault();

      var code = 'VC' + String(Math.floor(10000000 + Math.random() * 90000000));
      var booking = document.querySelector('input[name="delivery_type"]:checked');
      var method = booking ? booking.value : 'click_collect';

      if (container) {
        container.innerHTML = '' +
          '<div class="text-center py-8">' +
            '<p class="text-xs font-bold uppercase text-red-600">Pedido registrado</p>' +
            '<h4 class="text-2xl font-black text-slate-900 mt-2">' + code + '</h4>' +
            '<p class="text-xs text-slate-500 mt-2">' +
              (method === 'click_collect'
                ? 'Retiro en taller · pago pendiente'
                : 'Despacho a domicilio · pago pendiente') +
            '</p>' +
          '</div>';
      }

      if (itemsStep) itemsStep.classList.remove('hidden');
      if (footer) footer.classList.add('hidden');
      window.StrongCart.clear();
    });
  }

  render();
})();
