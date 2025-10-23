import * as api from './api.js';
import * as layout from './layout.js';

function debounce(func, delay) { let timeoutId; return function(...args) { clearTimeout(timeoutId); timeoutId = setTimeout(() => { func.apply(this, args); }, delay); }; }

// --- ZMIANA: Inicjalizacja stanu na podstawie sessionStorage ---
const state = {
    currentPage: sessionStorage.getItem('activePage') || 'deliveries',
    deliveries: { filters: { warehouse_id: '', statuses: [] } },
    stock: { filters: { warehouse_id: '', sku: '', status_of_total_qty: '' } },
    stockExpDate: { filters: { warehouse_id: '', sku: '', exp_date: '' } } // nowa strona
};

function navigateTo(page) {
    sessionStorage.setItem('activePage', page);
    if (state.currentPage === page && document.getElementById(`${page}-page`).querySelector('main')?.innerHTML.trim() !== '') { return; }
    state.currentPage = page;
    document.querySelectorAll('.page-container').forEach(p => p.classList.add('hidden'));
    document.getElementById(`${page}-page`).classList.remove('hidden');
    document.querySelectorAll('#main-nav .nav-link').forEach(link => link.classList.toggle('active', link.dataset.page === page));
    if (page === 'deliveries') { loadOrders(); }
    else if (page === 'stock-summary') { loadStockSummary(); }
    else if (page === 'stock-exp-date') { loadStockExpDate(); } // nowa strona
}

async function loadOrders() {
    layout.showLoading();
    document.getElementById('orders-container').innerHTML = '';
    try { const orders = await api.getOrders(state.deliveries.filters); layout.renderOrders(orders); }
    catch (error) { console.error('Błąd ładowania zamówień:', error); alert(`Wystąpił błąd ładowania zamówień: ${error.message}`); }
    finally { layout.hideLoading(); }
}

async function loadStockSummary() {
    layout.showLoading();
    try { const stockData = await api.getStockSummary(state.stock.filters); layout.renderStockSummaryTable(stockData); }
    catch (error) { console.error('Błąd ładowania stanów:', error); if (error.message.toLowerCase().includes('not found')) { layout.renderStockSummaryTable([]); } else { alert(`Wystąpił błąd ładowania stanów: ${error.message}`); } }
    finally { layout.hideLoading(); }
}

// nowa funkcja do strony stock-exp-date
async function loadStockExpDate() {
    layout.showLoading();
    document.getElementById('stock-exp-container').innerHTML = '';
    try {
        const data = await api.getStockWithExpDate(state.stockExpDate.filters);
        layout.renderStockExpDateTable(data);
    } catch (error) {
        console.error('Błąd ładowania stanów z datami:', error);
        alert(`Wystąpił błąd ładowania stanów z datami: ${error.message}`);
    } finally { layout.hideLoading(); }
}

function handleDeliveriesFilterChange() {
    const form = document.getElementById('deliveries-filters-form');
    state.deliveries.filters.warehouse_id = form.elements['warehouse_id'].value;
    const statuses = form.elements.statuses;
    state.deliveries.filters.statuses = statuses ? Array.from(statuses).filter(cb => cb.checked).map(cb => cb.value) : [];
    loadOrders();
}

function handleStockFilterChange() {
    const form = document.getElementById('stock-filters-form');
    state.stock.filters.warehouse_id = form.elements['warehouse_id'].value;
    state.stock.filters.sku = form.elements['sku'].value;
    state.stock.filters.status_of_total_qty = form.elements['status_of_total_qty'].value;
    loadStockSummary();
}

// nowy handler filtrów stock-exp-date
function handleStockExpFilterChange() {
    const form = document.getElementById('stock-exp-filters-form');
    state.stockExpDate.filters.warehouse_id = form.elements['warehouse_id'].value;
    state.stockExpDate.filters.sku = form.elements['sku'].value;
    state.stockExpDate.filters.exp_date = form.elements['exp_date'].value;
    loadStockExpDate();
}

async function handleUpdateAction(apiFunction, successMsg, errorMsg) {
    const whId = document.getElementById('stock-filter-warehouse-id').value || prompt("Please put active Warehouse ID::");
    if (!whId || isNaN(parseInt(whId))) { if(whId !== null) alert("Wrong Warehouse ID. Action cancelled."); return; }
    if (!confirm(`Are you sure that you want to make this operation for Warehouse #${whId}?`)) { return; }
    try { const result = await apiFunction(whId); alert(successMsg(result)); state.stock.filters.warehouse_id = whId; document.getElementById('stock-filter-warehouse-id').value = whId; loadStockSummary(); }
    catch (error) { alert(`${errorMsg}: ${error.message}`); }
}

async function handleContainerClick(event) {
    const actionElement = event.target.closest('[data-action]');
    if (!actionElement) return;
    const { action, orderId, productSku, currentQty } = actionElement.dataset;
    if (actionElement.closest('#deliveries-page')) {
        switch (action) {
            case 'add-product': document.getElementById('add-product-order-id').value = orderId; layout.showModal('add-product-modal'); break;
            case 'delete-order': if (confirm(`Czy na pewno chcesz usunąć CAŁE zamówienie #${orderId}?`)) { try { await api.deleteOrder(orderId); await loadOrders(); } catch (error) { alert(`Błąd usuwania zamówienia: ${error.message}`); } } break;
            case 'delete-product': if (confirm(`Czy na pewno chcesz usunąć produkt SKU ${productSku} z zamówienia #${orderId}?`)) { try { await api.deleteProductFromOrder({ inbound_order_id: orderId, product_sku: productSku }); await loadOrders(); } catch (error) { alert(`Błąd usuwania produktu: ${error.message}`); } } break;
            case 'change-status': const newStatus = prompt(`Wybierz nowy status dla zamówienia #${orderId}:\n\n${layout.STATUSES.join(', ')}`); if (newStatus && layout.STATUSES.includes(newStatus.toLowerCase())) { try { await api.updateOrderStatus({ order_id: orderId, status: newStatus.toLowerCase() }); await loadOrders(); } catch (error) { alert(`Błąd zmiany statusu: ${error.message}`); } } else if (newStatus !== null) { alert('Wybrano nieprawidłowy status.'); } break;
            case 'edit-product-qty': const newQty = prompt(`Podaj nową ilość dla produktu SKU: ${productSku}`, currentQty); if (newQty && !isNaN(newQty) && parseInt(newQty, 10) >= 0) { try { await api.updateProductQty({ order_id: parseInt(orderId, 10), sku: productSku, qty: parseInt(newQty, 10) }); await loadOrders(); } catch (error) { alert(`Błąd aktualizacji ilości: ${error.message}`); } } else if (newQty !== null) { alert('Wprowadź poprawną liczbę (0 lub więcej).'); } break;
        }
    }
    if (action === 'close-modal') { actionElement.closest('.modal')?.classList.add('hidden'); }
}

async function handleFormSubmit(event, apiFunction, modalId) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    try { await apiFunction(data); layout.hideModal(modalId); form.reset(); await loadOrders(); }
    catch (error) { alert(`Błąd operacji: ${error.message}`); }
}

function initialize() {
    document.getElementById('main-nav').addEventListener('click', (e) => { e.preventDefault(); const link = e.target.closest('.nav-link'); if (link?.dataset.page) navigateTo(link.dataset.page); });
    layout.renderStatusFilters();
    document.getElementById('deliveries-filters-form').addEventListener('input', handleDeliveriesFilterChange);
    document.getElementById('reset-deliveries-filters-btn').addEventListener('click', () => { document.getElementById('deliveries-filters-form').reset(); handleDeliveriesFilterChange(); });
    document.getElementById('show-create-order-modal-btn').addEventListener('click', () => layout.showModal('create-order-modal'));
    document.getElementById('create-order-form').addEventListener('submit', (e) => handleFormSubmit(e, api.createOrder, 'create-order-modal'));
    document.getElementById('add-product-form').addEventListener('submit', (e) => handleFormSubmit(e, api.addProductToOrder, 'add-product-modal'));

    const debouncedStockFilterHandler = debounce(handleStockFilterChange, 500);
    document.getElementById('stock-filters-form').addEventListener('input', debouncedStockFilterHandler);
    document.getElementById('reset-stock-filters-btn').addEventListener('click', () => { document.getElementById('stock-filters-form').reset(); handleStockFilterChange(); });

    const debouncedStockExpFilterHandler = debounce(handleStockExpFilterChange, 500);
    document.getElementById('stock-exp-filters-form')?.addEventListener('input', debouncedStockExpFilterHandler);
    document.getElementById('reset-stock-exp-filters-btn')?.addEventListener('click', () => { document.getElementById('stock-exp-filters-form')?.reset(); handleStockExpFilterChange(); });

    document.getElementById('update-stock-btn').addEventListener('click', () => handleUpdateAction(api.updateStockData, (r) => `Congrats! Stock updated. Processed: ${r.rows_number} rows.`, 'Error in stock update'));
    document.getElementById('update-inbound-qty-btn').addEventListener('click', () => handleUpdateAction(api.updateInboundQty, (r) => `Yupi! Updated qty of product in deliveries. Updated ${r.updated_sku_qty} SKU, total qty: ${r.updated_qty}.`, 'Error in inbound qty update'));ok

    document.body.addEventListener('click', handleContainerClick);

    navigateTo(state.currentPage);
}

document.addEventListener('DOMContentLoaded', initialize);