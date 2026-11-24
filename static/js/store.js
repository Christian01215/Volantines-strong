/*
 * Volantines Strong — catálogo, filtros, ficha de producto y puente al carrito.
 * Reconstruido para conservar la etiqueta <script src="js/store.js"> original.
 */
(function () {
  'use strict';

  var NS = window.StrongStore || window;
  var cards = function () {
    return Array.prototype.slice.call(
      document.querySelectorAll('#products-grid .shop-card')
    );
  };

  var currentProduct = null;

  function productFromCard(card) {
    var data = card.dataset;
    return {
      id: data.id,
      name: data.name,
      category: data.category,
      price: Number(data.price) || 0,
      priceLabel: data.priceLabel || NS.formatCLP(data.price),
      image: data.image || '',
      gallery: (data.gallery || '').split('|').filter(Boolean),
      specs: data.specs || '',
      description: data.description || '',
      stock: Number(data.stock) || 0,
      slug: data.slug || ''
    };
  }

  function applyFilters() {
    var search = NS.byId('search-input');
    var query = search ? search.value.trim().toLowerCase() : '';
    var active = document.querySelector('#category-filters .cat-btn.is-active');
    var category = active ? active.dataset.cat : 'ALL';

    cards().forEach(function (card) {
      var data = card.dataset;
      var text = (data.name + ' ' + data.specs + ' ' + data.category).toLowerCase();
      var matchesQuery = !query || text.indexOf(query) !== -1;
      var matchesCategory = category === 'ALL' || data.category === category;
      card.style.display = matchesQuery && matchesCategory ? '' : 'none';
    });
  }

  var searchInput = NS.byId('search-input');
  if (searchInput) {
    searchInput.addEventListener('input', applyFilters);
  }

  document.querySelectorAll('#category-filters .cat-btn').forEach(function (button) {
    button.addEventListener('click', function () {
      document.querySelectorAll('#category-filters .cat-btn').forEach(function (other) {
        other.classList.remove('is-active');
      });
      button.classList.add('is-active');
      applyFilters();
    });
  });

  var modal = NS.byId('product-modal');
  var modalTrack = NS.byId('modal-gallery-track');
  var modalGalleryIndex = 0;

  function updateModalGallery() {
    if (!modalTrack) return;
    var total = modalTrack.querySelectorAll('.modal-slide').length || 1;
    var counter = NS.byId('modal-gallery-counter');
    if (counter) counter.textContent = (modalGalleryIndex + 1) + ' / ' + total;
    var prev = NS.byId('modal-gallery-prev');
    var next = NS.byId('modal-gallery-next');
    if (prev) prev.style.display = total > 1 ? '' : 'none';
    if (next) next.style.display = total > 1 ? '' : 'none';
  }

  function goToModalSlide(index) {
    if (!modalTrack) return;
    var slides = Array.prototype.slice.call(modalTrack.querySelectorAll('.modal-slide'));
    if (!slides.length) return;
    modalGalleryIndex = Math.max(0, Math.min(slides.length - 1, index));
    var slide = slides[modalGalleryIndex];
    modalTrack.scrollTo({
      left: slide.offsetLeft - modalTrack.offsetLeft,
      behavior: 'smooth'
    });
    updateModalGallery();
  }

  function renderModalGallery(product) {
    if (!modalTrack) return;
    var urls = product.gallery && product.gallery.length
      ? product.gallery
      : (product.image ? [product.image] : []);
    modalGalleryIndex = 0;
    modalTrack.innerHTML = '';
    urls.forEach(function (url, index) {
      var slide = document.createElement('div');
      slide.className = 'modal-slide w-full shrink-0 snap-center grid place-items-center h-full';
      var image = document.createElement('img');
      image.src = url;
      image.alt = product.name + (index ? ' ' + (index + 1) : '');
      image.className = 'w-full h-full object-contain';
      slide.appendChild(image);
      modalTrack.appendChild(slide);
    });
    modalTrack.scrollLeft = 0;
    updateModalGallery();
  }

  var modalPrevBtn = NS.byId('modal-gallery-prev');
  if (modalPrevBtn) {
    modalPrevBtn.addEventListener('click', function () { goToModalSlide(modalGalleryIndex - 1); });
  }
  var modalNextBtn = NS.byId('modal-gallery-next');
  if (modalNextBtn) {
    modalNextBtn.addEventListener('click', function () { goToModalSlide(modalGalleryIndex + 1); });
  }
  if (modalTrack) {
    modalTrack.addEventListener('scroll', function () {
      var slides = Array.prototype.slice.call(modalTrack.querySelectorAll('.modal-slide'));
      if (!slides.length) return;
      var closest = 0;
      var minDistance = Infinity;
      slides.forEach(function (slide, index) {
        var distance = Math.abs((slide.offsetLeft - modalTrack.offsetLeft) - modalTrack.scrollLeft);
        if (distance < minDistance) {
          minDistance = distance;
          closest = index;
        }
      });
      if (closest !== modalGalleryIndex) {
        modalGalleryIndex = closest;
        updateModalGallery();
      }
    });
  }

  function openModal(product) {
    if (!modal) return;
    currentProduct = product;

    var cat = NS.byId('modal-cat');
    var title = NS.byId('modal-title');
    var price = NS.byId('modal-price');
    var stock = NS.byId('modal-stock');
    var desc = NS.byId('modal-desc');
    var specs = NS.byId('modal-specs');
    var wa = NS.byId('modal-wa-btn');
    var customize = NS.byId('modal-customize-btn');

    renderModalGallery(product);
    if (cat) cat.textContent = product.category;
    if (title) title.textContent = product.name;
    if (price) price.textContent = product.priceLabel;
    if (stock) {
      stock.textContent = product.stock > 0
        ? 'STOCK DISPONIBLE: ' + product.stock
        : 'SIN STOCK';
    }
    var qty = NS.byId('modal-qty');
    if (qty) {
      qty.max = String(Math.max(1, Number(product.stock) || 1));
      qty.value = '1';
    }
    if (desc) desc.textContent = product.specs || 'Sin ficha técnica cargada.';
    if (specs) specs.textContent = product.description || 'Sin descripción cargada.';
    if (wa) {
      var waBase = window.STRONG_WHATSAPP_URL;
      if (waBase && waBase !== '#') {
        wa.href = waBase + '?text=' + encodeURIComponent(
          'Hola, quiero consultar por ' + product.name + ' (' + product.category + ')'
        );
      } else {
        wa.href = '#';
      }
    }

    if (customize) {
      var customizeUrl = (window.STRONG_CART_URLS || {}).customize;
      var isReel = product.category.toLowerCase().indexOf('carrete') !== -1;
      if (isReel && customizeUrl && product.slug) {
        customize.href = customizeUrl.replace('SLUG', product.slug);
        customize.classList.remove('hidden');
      } else {
        customize.classList.add('hidden');
      }
    }

    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }

  function closeModal() {
    if (!modal) return;
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    currentProduct = null;
  }

  var closeModalBtn = NS.byId('close-product-modal');
  if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
  if (modal) {
    modal.addEventListener('click', function (event) {
      if (event.target === modal) closeModal();
    });
  }

  cards().forEach(function (card) {
    var product = productFromCard(card);

    var imageButton = card.querySelector('[data-action="detail"], .shop-image-button');
    if (imageButton) {
      imageButton.addEventListener('click', function () {
        openModal(product);
      });
    }

    var addButton = card.querySelector('[data-action="add"], .shop-add');
    if (addButton) {
      addButton.addEventListener('click', function (event) {
        event.stopPropagation();
        if (window.StrongCart) window.StrongCart.add(product);
      });
    }
  });

  var modalAdd = NS.byId('modal-add-btn');
  if (modalAdd) {
    modalAdd.addEventListener('click', function () {
      if (currentProduct && window.StrongCart) {
        var qtyInput = NS.byId('modal-qty');
        window.StrongCart.add(currentProduct, null, qtyInput ? qtyInput.value : 1);
        closeModal();
      }
    });
  }

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') closeModal();
  });
})();
