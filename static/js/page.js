$(function() {

table= $('#jpk').on('init.dt', function() {
		poll_status();
	}).DataTable({
	
	"language": {
    	"url": "/static/DataTables/Polish.json"
    },
	
	ajax: "/ajax"+window.location.pathname+"jpk/lista/",   
	
	columns: [
    	{ data: 'numer' },
    	{ data: 'utworzony' },
    	{ data: 'kod' },
    	{ data: 'dataod' },
    	{ data: 'datado' },
    	{ data: 'opis' },
    	{ data: 'stan' }
	],  
    columnDefs: [
        { "width": "25%", "targets": 5 }
    ],	
    info: false,
	stateSave: true,
 	lengthMenu: [10, 15, 20, 100],
 	pageLength: 15,
    createdRow: function ( row, data, index ) {
    	if(data.stan == 'W KOLEJCE' || data.stan == 'TWORZENIE')
    		timer_add(index, data.numer, data.czas);
    	$(row).attr('id', 'tr_'+data.numer);
    	if(data.stan == 'DOSTARCZONY')
    		$('td', row).eq(6).addClass('hl_green');
    	if(data.stan == 'NIE WYSŁANY' || data.stan == 'NIE PRZYJĘTY' || data.stan == 'BŁĄD WYSYŁKI')
    		$('td', row).eq(6).addClass('hl_red'); 
    	if(data.bledy == 'True') 
    		$('td', row).eq(6).addClass('hl_bledy');  
    },
	order: [[ 0, 'desc' ]]    
});

var firmy= $('#firmy').DataTable({
	"language": {
    	"url": "/static/DataTables/Polish.json"
    },
	
	ajax: "/ajax/firmy/",   
	
	columns: [
    	{ data: 'oznaczenie' },
    	{ data: 'nazwa' },
    	{ data: 'adres' },
    	{ data: 'nip' },
    	{ data: 'kod_urzedu' },     	
	],  
    
    columnDefs: [
        { "width": "5%", "targets": 0 }
    ],
    	
    info: false,
	stateSave: true,
 	lengthMenu: [10, 15, 20, 100],	
 	pageLength: 15,
	order: [[ 0, 'asc' ]]    
});
   
faktury= $('#faktury').DataTable({
	
	"language": {
    	"url": "/static/DataTables/Polish.json"
    },
	
	ajax: "/bra/ajax/faktury/",   
	
	columns: [
    	{ data: 'faktura' },
    	{ data: 'daty' },
    	{ data: 'nip' },
    	{ data: 'nazwa' },
    	{ data: 'adres' },
    	
    	{ data: 'sprzedaz23' },
    	{ data: 'sprzedaz8' },
    	{ data: 'sprzedaz5' },
    	{ data: 'sprzedaz0zw' },
    	{ data: 'naleznosc' },
    	
    	{ data: 'rodzaj' }
	],  
	
    columnDefs: [
        { "width": "40px", "targets": 1 },    
        { "width": "20%", "targets": [3, 4] },
        { "sClass": "ar", "targets": [ 5, 6, 7, 8, 9 ] }               
    ],
    	
    info: false,
	stateSave: true,
 	lengthMenu: [10, 15, 20, 100],
 	pageLength: 10,
 	
	order: [[ 0, 'asc' ]]    
});

$('#firmy tbody').on('click', 'tr[role="row"]', function () {
	var tr = $(this).closest('tr');
	var row = firmy.row( tr );
	d= row.data();
	window.location.href = "/"+d.oznaczenie+'/';
} );
    
    
$('#jpk tbody').on('click', 'tr[role="row"]', function () {
	var tr = $(this).closest('tr');
	var row = table.row( tr );
 
	if ( row.child.isShown() ) {
		row.child.hide();
		tr.removeClass('shown');
	}
	else {
		d= row.data();
		$.ajax({
			dataType: "html",
			url: '/jpk/'+d.numer+'/rozwin/',
			success: function(data) {
		        row.child(data).show();
		        tr.addClass('shown');
			} 
		});
	}
});
    
$("#jpk_wb").click(function() {
 	$("#rachunki").toggle();
}); 

$("#jpk_mag").click(function() {
 	$("#magazyny").toggle();
});

$(".naglowek-paczki").first().next().toggle();

$("span.tog").click(function() {
 	$(this).parent().next().toggle();
}); 

$(document).on("click", ".dodaj-paczke", function () {
     var paczkaId = $(this).data('paczka');
     $(".modal-body #paczka").val( paczkaId );
	 $('#plik-modal').modal('show');     
});

$(document).on("click", ".jpk-przygotuj", function () 
{
	$('#initupload-modal').modal('hide');  
	var jpk_id= $(this).parent().find('#initupload_jpk_id').val();
	
	var row= table.row($('#tr_'+jpk_id));
	setTimeout(function() { 
		refresh_row(row);
		show_details(row); 
	}, 2000);
});

$(document).on("click", ".plik-upload", function () 
{
     var jpk_id = $(this).data('jpk_id');
     $("#jpk_id").val( jpk_id );
	 $('#upload-modal').modal('show');     
});

$(document).on("click", ".plik-initupload", function () 
{
     var jpk_id = $(this).data('jpk_id');
     $("#initupload_jpk_id").val( jpk_id );
	 $('#initupload-modal').modal('show');     
});

$(document).on("click", ".jpk-nazwa", function () 
{
     $("#nazwa-jpk_id").val($(this).data('jpk_id'));
     $("#id_nazwa").val($(this).data('nazwa'));
	 $('#nazwa-modal').modal('show');
});

$('.modal').on('shown.bs.modal', function () {
    $(this).find('input:text:visible:first').focus();
})

$("#pliki-form").submit(function( event ) {
	if(!poprawneDane()) {
		event.preventDefault();
	}
});

$(document).on("click", "li.disabled", function(event) {
	event.preventDefault();
	return false;
});

$(".alert").slideDown('slow', function(){});
$(".alert").click(function() {
	$(this).slideUp({}, 'slow', function(){$(this).remove();});
});

$('#initupload-form').on('submit', function() {
	if($('#id_plik').get(0).files.length === 0)
    	return false;
});

});
