$(function() {

if($('#jpk').length) {

table= $('#jpk').on('init.dt', function() {
		poll_status();
		rozwiniecie();
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

}

if($('#firmy').length) {

var firmy= $('#firmy').DataTable({
	"language": {
    	"url": "/static/DataTables/Polish.json"
    },
	
	ajax: "/ajax/firmy/",   
	
	columns: [
    	{ data: 'oznaczenie' },
    	{ data: 'nazwa' },
		{ data: 'kod' },
		{ data: 'okres' },
		{ data: 'opis' },
		{ data: 'stan' },
	],  
    
    columnDefs: [
        { "width": "5%", "targets": 0 }
    ],
    	
    info: false,
	stateSave: true,
 	lengthMenu: [10, 15, 20, 100],	
 	pageLength: 20,
	order: [[ 0, 'asc' ]]    
});
  
}

if($('#fakturyl').length) {

faktury= $('#fakturyl').DataTable({
	
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

}

$('#firmy tbody').on('click', 'tr[role="row"]', function () {
	var tr = $(this).closest('tr');
	var row = firmy.row( tr );
	d= row.data();
	window.location.href = "/"+d.oznaczenie+'/';
} );
    
    
$('#jpk tbody').on('click', 'tr[role="row"]', function () {
	rozwin(this);
});

function rozwin(tr_this, tr_id) 
{
	var tr = $(tr_this).closest('tr');
	var row = table.row( tr );
 
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
		d= row.data();
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
    
function rozwiniecie() {
	if (tr_id)
		rozwin($("tr#tr_"+tr_id)[0], tr_id);
}

$("#jpk_wb").click(function() {
 	$("#rachunki").toggle();
}); 

$("#jpk_mag").click(function() {
 	$("#magazyny").toggle();
});

$("#przeplywy").click(function() {
 	$("#metoda_przeplywow").toggle();
});

$("#jpk_sf").click(function() {
 	$("#sprawozdanie").toggle();
 	if($('#sprawozdanie').is(':visible')) {
 		rok= new Date().getFullYear()-1;
 		poczatek= new Date(rok+'-01-01');
 		koniec= new Date(rok+'-12-31');
 		$('#dataod').val(poczatek.toISOString().substring(0,10));
 		$('#datado').val(koniec.toISOString().substring(0,10));
 	}
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

$(document).on("click", ".sf-upload", function () 
{
     var jpk_id = $(this).data('jpk_id');
     $("#sf-jpk_id").val( jpk_id );
	 $('#sf-modal').modal('show');     
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

function alertSetup() {
	$(".alert").slideDown('slow', function() {
		// Timeout to hide the message, can be set in alert element 
		// with data-timeout attribute
		timeout= $(this).data('timeout') || 2000;
		setTimeout(() => {
			// After 'timeout' millis message is removed
			$(this).slideUp('slow', () => $(this).remove());
		}, timeout);
	});
	
	$(".alert").click(function() {
		$(this).slideUp('slow', () => $(this).remove());
	});
}

alertSetup();

$('#initupload-form').on('submit', function() {
	if($('#id_plik').get(0).files.length === 0)
    	return false;
});

$("#oznaczenie").change(function() {
	$.getJSON("/ajax/"+$("#oznaczenie").val()+"/dane/", function(data) {
		$('#nazwa').val(data.nazwa);
		$('#nip').val(data.nip);		
	});
});

$(document).on("click", "input.cancel", function () {
	window.location.href= $(this).data("url");
});

$("#konto_kon").change(function() {
	if($("#konto_kon").val()) {
		$.getJSON("/bra/ajax/"+$("#id_firma").val()+"/konto/"+$("#konto_kon").val()+"/", function(data) {
		if(data.errors) 
			$("#konto_spr-div").addClass("has-error");	
		else
			$("#konto_spr-div").removeClass("has-error");		
		$("#konto_kon-help").html(data.nazwa);
		});
	}
	else
		$("#konto_kon-help").html('');	
});

$("#konto_spr").change(function() {
	$.getJSON("/bra/ajax/"+$("#id_firma").val()+"/konto/"+$("#konto_spr").val()+"/", function(data) {
		if(data.errors) 
			$("#konto_spr-div").addClass("has-error");	
		else
			$("#konto_spr-div").removeClass("has-error");						
		$("#konto_spr-help").html(data.nazwa);
	});
});

$(window).on("beforeunload", function(e) {
	if (window.app && !window.app.zapisane())
		return "Dane nie zostały zapisane";
});


window.jpk_log= function(message, level, timeout) {
	$('.main-container').prepend(
		`<div class="alert alert-${level}" role="alert" data-timeout="${timeout}">${message}</div>`
	);
	alertSetup();	
};

window.jpk_error= function(message, error) {
	jpk_log(`${message}: ${error}`, 'danger', 4000);
}

window.jpk_info= function(message) {
	jpk_log(message, 'success', 2000);
}

});
