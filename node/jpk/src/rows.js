// Pobranie rozwinięcia wiersza
export function show_details(row) {

	$.ajax({
		dataType: "html",
		url: '/jpk/'+row.data().numer+'/rozwin/',
		success: function(data) {
	        row.child(data).show();
	        $(row).addClass('shown');
		} 
	});
}

// Odświeżenie danych wiersza
export function refresh_row(row) {

	$.ajax({
		dataType: "json",
		url: '/jpk/'+row.data().numer+'/refresh/',
		success: function(row_data) {
	        row.data(row_data);
	        row.invalidate();
		} 
	});
}

// Rozwinięcie lub zwinięcie danego wiersza
export function rozwin(tr_this, tr_id) 
{
	const tr = $(tr_this).closest('tr');
	const row = table.row( tr );
    const d= row.data();
 
	if ( row.child.isShown() ) {
		row.child.hide();
        tr.removeClass('shown');
		$.ajax({
			dataType: "json",
			url: '/jpk/'+(tr_id||d.numer)+'/zwin/',
			success: function(data) {
		        row.child(data).show();
		        tr.addClass('shown');
			} 
		});		
	}
	else {
		$.ajax({
			dataType: "html",
			url: '/jpk/'+(tr_id||d.numer)+'/rozwin/',
			success: function(data) {
		        row.child(data).show();
		        tr.addClass('shown');
			} 
		});
	}
}