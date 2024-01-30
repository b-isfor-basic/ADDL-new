document.getElementById("search").addEventListener("input", (e) => {
  let filter = e.target.value.toLowerCase();
  const tables = document.getElementsByTagName("table");

  Array.from(tables).forEach((table) => {
    Array.from(table.tBodies[0]?.rows || []).forEach((row) => {
      row?.classList.toggle("highlight", row?.getElementsByTagName("td")[1]?.textContent.toLowerCase().includes(filter));
    });
  });
});
