
export function kwota_display(kwota) {
    return kwota?kwota.toLocaleString('pl-PL', {minimumFractionDigits: 2, useGrouping: true}):'';
}

export function text_to_kwota_display(value /*, grouping= true*/) {
    let v= value.trim();
    if (v.length === 0) return v;

    v= v.replace(/\s/g, '').replace(',', '.');
    let num= Number(v);

    if (isNaN(v)) return '';

    v= parseFloat(Math.round(num * 100) / 100).toFixed(2);
    v= parseFloat(v).toLocaleString('pl-PL', {minimumFractionDigits: 2, useGrouping: true});
    if (v==='0,00') v= '';
    return v;
}
    
export function text_to_number(value) {
    let v= value.trim().replace(/\s/g, '');
    v= v.replace(',', '.');
    v= parseFloat(v);
    let num= Number(v);
    if (isNaN(v))
    {
        num= 0.00;
        // parseFloat(Math.round(a * 100) / 100).toFixed(2);
        // a= parseFloat(a).toLocaleString('pl-PL');
    }
    return num;
}
