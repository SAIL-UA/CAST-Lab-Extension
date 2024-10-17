export function createAlert(doc: Document, message: string, classList: string[]){
  let el = doc.createElement('div');
  const text = doc.createTextNode(message);
  el.appendChild(text);
  for (let i = 0; i < classList.length; i++)
    el.classList.add(classList[i]);
  let main = doc.getElementById('main');
  main?.appendChild(el);

  return el;
}