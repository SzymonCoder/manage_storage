// --- WSPÓLNA FUNKCJA ---
async function handleResponse(response) {
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: `Błąd serwera. Status: ${response.status}` }));
        throw new Error(errorData.detail || errorData.message || `HTTP error! status: ${response.status}`);
    }
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
        return response.json();
    }
    return {};
}

// --- SEKCJA DOSTAW ---
const DELIVERIES_API_URL = '/api/order_inbound';

export async function getOrders(filters = {}) {
    const params = new URLSearchParams();
    if (filters.warehouse_id) params.append('warehouse_id', filters.warehouse_id);
    if (filters.statuses && filters.statuses.length > 0) {
        filters.statuses.forEach(status => params.append('statuses', status));
    }
    const response = await fetch(`${DELIVERIES_API_URL}/all?${params.toString()}`);
    return handleResponse(response);
}

export async function createOrder(data) {
    const response = await fetch(`${DELIVERIES_API_URL}/create_order`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    return handleResponse(response);
}

export async function addProductToOrder(data) {
    const response = await fetch(`${DELIVERIES_API_URL}/add_product_to_order`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    return handleResponse(response);
}

export async function updateOrderStatus(data) {
    const response = await fetch(`${DELIVERIES_API_URL}/update_product_status_in_order`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    return handleResponse(response);
}

export async function updateProductQty(data) {
    const response = await fetch(`${DELIVERIES_API_URL}/update_qty_sku_in_order`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    return handleResponse(response);
}

export async function deleteOrder(orderId) {
    const response = await fetch(`${DELIVERIES_API_URL}/delete_order/${orderId}`, { method: 'DELETE' });
    return handleResponse(response);
}

export async function deleteProductFromOrder(data) {
    const response = await fetch(`${DELIVERIES_API_URL}/delete_product_in_order`, { method: 'DELETE', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    return handleResponse(response);
}

// --- SEKCJA STANÓW MAGAZYNOWYCH ---
const STOCK_API_URL = '/api/stock_summary';
const STOCK_EXP_API_URL = '/api/stock_exp_date';

export async function getStockSummary(filters = {}) {
    let url = `${STOCK_API_URL}`;
    if (filters.warehouse_id && filters.sku) {
        url += `/${filters.warehouse_id}/sku/${filters.sku}`;
    } else if (filters.warehouse_id && filters.status_of_total_qty) {
        url += `/${filters.warehouse_id}/status/${filters.status_of_total_qty}`;
    } else if (filters.warehouse_id) {
        url += `/${filters.warehouse_id}`;
    } else {
        url += `/all`;
    }
    const response = await fetch(url);
    return handleResponse(response);
}

export async function getStockWithExpDate(filters = {}) {
    let url = `${STOCK_EXP_API_URL}/all`;
    const params = new URLSearchParams();
    if (filters.warehouse_id) params.append('warehouse_id', filters.warehouse_id);
    if (filters.sku) params.append('sku', filters.sku);
    if (filters.exp_date) params.append('exp_date', filters.exp_date);
    if ([...params].length > 0) url += `?${params.toString()}`;
    const response = await fetch(url);
    return handleResponse(response);
}

export async function updateStockData(warehouseId) {
    const response = await fetch(`${STOCK_API_URL}/update/${warehouseId}`, { method: 'POST' });
    return handleResponse(response);
}

export async function updateInboundQty(warehouseId) {
    const response = await fetch(`${STOCK_API_URL}/update_stock_inbound_qty/${warehouseId}`, { method: 'POST' });
    return handleResponse(response);
}



// --- SEKCJA STOCK_WITH_EXP_DATE ---
const STOCK_WITH_EXP_DATE_API_URL = '/api/stock_with_exp_date';

// 1. Pobierz wszystkie dane stock_with_exp_date
export async function getAllStockWithExpDate() {
    const response = await fetch(`${STOCK_WITH_EXP_DATE_API_URL}/all`);
    return handleResponse(response);
}

// 2. Pobierz dane stock_with_exp_date według ID magazynu
export async function getStockWithExpDateByWarehouseId(warehouseId) {
    const response = await fetch(`${STOCK_WITH_EXP_DATE_API_URL}/warehouse/${warehouseId}`);
    return handleResponse(response);
}

// 3. Pobierz dane stock_with_exp_date według statusu ilości
export async function getStockWithExpDateByQtyStatus(qtyStatus) {
    const response = await fetch(`${STOCK_WITH_EXP_DATE_API_URL}/status/${qtyStatus}`);
    return handleResponse(response);
}

// 4. Pobierz dane stock_with_exp_date według SKU
export async function getStockWithExpDateBySku(sku) {
    const response = await fetch(`${STOCK_WITH_EXP_DATE_API_URL}/sku/${sku}`);
    return handleResponse(response);
}