const loader = document.getElementById('loader');
export function showLoading() { loader.classList.remove('hidden'); }
export function hideLoading() { loader.classList.add('hidden'); }
export function showModal(modalId) { document.getElementById(modalId)?.classList.remove('hidden'); }
export function hideModal(modalId) { document.getElementById(modalId)?.classList.add('hidden'); }

const ordersContainer = document.getElementById('orders-container');
export const STATUSES = ["created", "approved", "produced", "in_transit", "delivered", "completed", "cancelled"];
const STATUS_COLORS = { created: 'bg-cyan-100 text-cyan-800', approved: 'bg-green-100 text-green-800', produced: 'bg-blue-100 text-blue-800', in_transit: 'bg-yellow-100 text-yellow-800', delivered: 'bg-purple-100 text-purple-800', completed: 'bg-gray-200 text-gray-800', cancelled: 'bg-red-100 text-red-800', default: 'bg-gray-100 text-gray-800' };
function getDeliveryStatusBadge(status) { const color = STATUS_COLORS[status] || STATUS_COLORS.default; return `<span class="px-2 py-1 text-xs font-medium rounded-full ${color}">${status}</span>`; }
export function renderStatusFilters() { const container = document.getElementById('status-filter-container'); if (!container) return; container.innerHTML = STATUSES.map(status => `<label class="flex items-center space-x-2 cursor-pointer"><input type="checkbox" name="statuses" value="${status}" class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"><span class="text-sm text-gray-700">${status}</span></label>`).join(''); }

function createProductRow(product, order) { return `<tr class="hover:bg-gray-50 border-b border-gray-200"><td class="p-3 text-sm text-gray-700">${order.inbound_order_id}</td><td class="p-3 text-sm text-gray-700">${product.inbound_order_product_id}</td><td class="p-3 text-sm text-gray-700 font-mono">${product.sku}</td><td class="p-3 text-sm text-gray-900 font-medium">${product.product_qty}</td><td class="p-3">${getDeliveryStatusBadge(order.status)}</td><td class="p-3 text-right"><div class="flex items-center justify-end space-x-2"><button class="btn-icon" title="Edytuj ilość" data-action="edit-product-qty" data-order-id="${order.inbound_order_id}" data-product-sku="${product.sku}" data-current-qty="${product.product_qty}"><i class="fas fa-pencil-alt text-gray-500 hover:text-blue-600"></i></button><button class="btn-icon" title="Usuń produkt" data-action="delete-product" data-order-id="${order.inbound_order_id}" data-product-sku="${product.sku}"><i class="fas fa-trash-alt text-gray-500 hover:text-red-600"></i></button></div></td></tr>`; }

function createOrderCard(order) { return `<div class="bg-white rounded-lg shadow-md overflow-hidden" data-order-id="${order.inbound_order_id}"><div class="p-4 border-b border-gray-200 flex flex-col sm:flex-row justify-between items-start sm:items-center"><div><h3 class="text-xl font-bold text-gray-800">Zamówienie #${order.inbound_order_id}</h3><p class="text-sm text-gray-500 mt-1">Dostawca: ${order.supplier_name} | Magazyn: ${order.warehouse_id}</p></div><div class="mt-3 sm:mt-0 flex items-center gap-4">${getDeliveryStatusBadge(order.status)}<div class="flex items-center gap-1"><button class="btn-icon" title="Dodaj produkt" data-action="add-product" data-order-id="${order.inbound_order_id}"><i class="fas fa-plus-circle text-lg text-green-500"></i></button><button class="btn-icon" title="Zmień status zamówienia" data-action="change-status" data-order-id="${order.inbound_order_id}"><i class="fas fa-edit"></i></button><button class="btn-icon" title="Usuń całe zamówienie" data-action="delete-order" data-order-id="${order.inbound_order_id}"><i class="fas fa-trash-alt text-red-500"></i></button></div></div></div><div class="p-4"><h4 class="text-md font-semibold mb-2 text-gray-600">Produkty w zamówieniu</h4>${order.products && order.products.length > 0 ? `<div class="overflow-x-auto"><table class="w-full"><thead class="bg-gray-50"><tr><th class="th-cell">ID Zam.</th><th class="th-cell">ID Linii</th><th class="th-cell">SKU</th><th class="th-cell">Ilość</th><th class="th-cell">Status Zam.</th><th class="th-cell text-right">Akcje</th></tr></thead><tbody>${order.products.map(p => createProductRow(p, order)).join('')}</tbody></table></div>` : `<p class="text-sm text-gray-500 italic">Brak produktów w tym zamówieniu.</p>`}</div></div>`; }

export function renderOrders(orders) {
    if (!ordersContainer) return;
    if (!orders || orders.length === 0) {
        ordersContainer.innerHTML = `<div class="text-center py-10 bg-white rounded-lg shadow-md"><i class="fas fa-box-open text-4xl text-gray-400"></i><p class="mt-4 text-gray-600 font-semibold">Nie znaleziono zamówień.</p><p class="text-sm text-gray-500">Spróbuj zmienić filtry lub dodaj nowe zamówienie.</p></div>`;
        return;
    }
    ordersContainer.innerHTML = orders.map(order => createOrderCard(order)).join('');
}

const stockSummaryContainer = document.getElementById('stock-summary-container');
const STOCK_STATUS_COLORS = { 'OK': 'bg-green-100 text-green-800', 'LOW': 'bg-yellow-100 text-yellow-800', 'EMPTY': 'bg-red-100 text-red-800', 'GOOD': 'bg-green-100 text-green-800', 'MEDIUM': 'bg-yellow-100 text-yellow-800', 'CRITICAL': 'bg-orange-100 text-orange-800', 'TOO_LOW': 'bg-red-100 text-red-800', 'default': 'bg-gray-100 text-gray-800' };
function getStockStatusBadge(status) { const color = STOCK_STATUS_COLORS[status] || STOCK_STATUS_COLORS.default; return `<span class="px-2 py-1 text-xs font-medium rounded-full ${color}">${status}</span>`; }
function createStockSummaryRow(item) { return `<tr class="border-b border-gray-200 hover:bg-gray-50"><td class="p-3 text-sm text-gray-700">${item.warehouse_id}</td><td class="p-3 text-sm text-gray-800 font-mono">${item.product_id}</td><td class="p-3 text-base text-gray-900 font-bold">${item.qty_total_of_sku}</td><td class="p-3 text-sm text-gray-700">${item.ordered_in_qty}</td><td class="p-3">${getStockStatusBadge(item.status_of_total_qty)}</td><td class="p-3 text-sm text-green-600">${item.good_date_qty}</td><td class="p-3 text-sm text-yellow-600">${item.medium_date_qty}</td><td class="p-3 text-sm text-orange-600">${item.critical_date_qty}</td><td class="p-3 text-sm text-red-600 font-semibold">${item.expired_qty}</td></tr>`; }
export function renderStockSummaryTable(data) {
    if (!stockSummaryContainer) return;
    let content;
    const items = Array.isArray(data) ? data : (data ? [data] : []);
    if (items.length === 0 || (items.length === 1 && Object.keys(items[0]).length === 0)) {
        content = `<div class="text-center py-10"><i class="fas fa-search text-4xl text-gray-400"></i><p class="mt-4 text-gray-600 font-semibold">Brak danych dla podanych filtrów.</p></div>`;
    } else {
        content = `<div class="overflow-x-auto"><table class="w-full">
            <thead class="bg-gray-50"><tr><th class="th-cell">ID Mag.</th><th class="th-cell">SKU</th><th class="th-cell">Ilość Total</th><th class="th-cell">W Dostawie</th><th class="th-cell">Status</th><th class="th-cell">Ilość OK</th><th class="th-cell">Ilość Med</th><th class="th-cell">Ilość Kryt.</th><th class="th-cell">Przeterm.</th></tr></thead>
            <tbody>${items.map(createStockSummaryRow).join('')}</tbody></table></div>`;
    }
    stockSummaryContainer.innerHTML = content;
}

// --- NOWA FUNKCJA DLA STOCK EXP DATE ---
const stockExpContainer = document.getElementById('stock-exp-container');
function createStockExpRow(item) {
    // Ustal wartości z fallbackami i alternatywnymi nazwami
    const warehouseId = item.warehouse_id || '-';
    const productId = item.product_id || '-';
    const qtyTotal = item.qty_total_of_sku ?? '-';
    const qtyPerExpDate = item.qty_per_exp_date ?? '-';
    const statusOfExpDate = item.status_of_exp_date || '-';
    const statusOfTotalQty = item.status_of_total_qty || '-';
    // Obsługa różnych nazw dla daty ważności
    const expirationDate = item.expiration_date || item.exp_date || '-';
    return `<tr class="border-b border-gray-200 hover:bg-gray-50">
        <td class="p-3 text-sm text-gray-700">${warehouseId}</td>
        <td class="p-3 text-sm text-gray-800 font-mono">${productId}</td>
        <td class="p-3 text-base text-gray-900 font-bold">${qtyTotal}</td>
        <td class="p-3 text-sm text-gray-700">${qtyPerExpDate}</td>
        <td class="p-3 text-sm text-gray-700">${statusOfExpDate}</td>
        <td class="p-3 text-sm text-gray-700">${statusOfTotalQty}</td>
        <td class="p-3 text-sm text-gray-700">${expirationDate}</td>
    </tr>`;
}
export function renderStockExpDateTable(data) {
    if (!stockExpContainer) return;
    let content;
    const items = Array.isArray(data) ? data : (data ? [data] : []);
    if (items.length === 0 || (items.length === 1 && Object.keys(items[0]).length === 0)) {
        content = `<div class="text-center py-10"><i class="fas fa-search text-4xl text-gray-400"></i><p class="mt-4 text-gray-600 font-semibold">Brak danych dla podanych filtrów.</p></div>`;
    } else {
        content = `<div class="overflow-x-auto"><table class="w-full">
            <thead class="bg-gray-50">
                <tr>
                    <th class="th-cell">ID Magazynu</th>
                    <th class="th-cell">ID Produktu</th>
                    <th class="th-cell">Ilość Total</th>
                    <th class="th-cell">Ilość na datę</th>
                    <th class="th-cell">Status daty</th>
                    <th class="th-cell">Status Total</th>
                    <th class="th-cell">Data Ważności</th>
                </tr>
            </thead>
            <tbody>${items.map(createStockExpRow).join('')}</tbody>
        </table></div>`;
    }
    stockExpContainer.innerHTML = content;
}