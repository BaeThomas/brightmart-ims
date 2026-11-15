function ProductTable({ products }) {
  return (
   <div
   className="table-wrapper"
   role="region"
   aria-label="Product stock table"
   tabIndex={0}
  >
      <table>
        <caption>Product stock information</caption>

        <thead>
          <tr>
            <th scope="col">Product</th>
            <th scope="col">SKU</th>
            <th scope="col">Category</th>
            <th scope="col">Current Stock</th>
            <th scope="col">Status</th>
          </tr>
        </thead>

        <tbody>
          {products.map((product) => (
            <tr key={product.id}>
              <td>{product.product_name}</td>
              <td>{product.sku}</td>
              <td>{product.category_name}</td>
              <td>{product.stock_quantity}</td>
              <td>
                {product.stock_quantity <= product.reorder_level
                  ? "Low stock"
                  : "In stock"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ProductTable;