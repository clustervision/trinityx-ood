
export function parseHtmlToData(htmlString: string) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(htmlString, 'text/html');
  const rows = doc.querySelectorAll('table tbody tr');
  const parsedData: any[] = [];

  rows.forEach((row) => {
    const cells = row.querySelectorAll('td');
    // Ensure row has data
    if (cells.length > 1) {
      parsedData.push({
        name: cells[1]?.innerText.trim() || 'Unknown',
        size: cells[2]?.innerText.trim(),
        order: cells[3]?.innerText.trim() || 'ascending',
        room: cells[4]?.innerText.trim() || '',
        site: cells[5]?.innerText.trim() || '',
      });
    }
  });

  return parsedData;
}