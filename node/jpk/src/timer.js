import { show_details } from './rows';

var timer= null;
var timed= [];

// Wyświetlanie czasu tworzenia pliku JPK
function timer_show(i) {

	const roznica= Math.round((new Date() - timed[i].browser)/1000);
	const s= timed[i].serwer.split(':');
	
	s[0]= parseInt(s[0]);
	s[1]= parseInt(s[1]);
	s[2]= parseInt(s[2]);
	
	s[2]= s[2] + roznica;
	if(s[2]>=60) {
		s[2]= s[2] - 60;
		s[1]= s[1] + 1;
		if(s[1]>=60) {
			s[1]= s[1]-60;
			s[0]= s[0]+1;
		}
	}
	
	const czas= s[0]+':'+checkTime(s[1])+':'+checkTime(s[2]);
	const stan= table.row(timed[i].id).data().stan;
    const f= stan.match(/([A-Z ]+)/);

	table.row(timed[i].id).data().stan= f[1].trim()+'<br/><span class="small">'+czas+'</span>';
	table.row(timed[i].id).invalidate();
}

// Wyświetlenie wszystkich timerów
function timer_run()  {

	if(timed.length>0) {
		for(let i=0; i<timed.length; i++) {
			timer_show(i);
		}
		timer= setTimeout(timer_run, 500);
	}
	else
		clearTimeout(timer)	
}		        

// Dodanie nowego timera
export function timer_add(index, jpk_id, serwer_czas)  {

	for(let i=0; i<timed.length; i++)
	{
		if(timed[i].id == index)
		{
			timed[i].serwer= serwer_czas;
			timed[i].browser= new Date();
			return;
		}
	}
	
	if(serwer_czas) {
		timed.push({
			id: index,
			jpk_id: jpk_id, 
			serwer: serwer_czas,
			browser: new Date()
		});
		if(timer) {
			clearTimeout(timer);
		}
		timer_run();
	}
}
    
// Usunięcie timera
function timer_del(jpk_id) {

	for(let i=0; i<timed.length; i++)
	{
		if(timed[i].jpk_id == jpk_id)
			timed.splice(i, 1);
	}
}

// Format godziny
function checkTime(i) {
	return (i < 10)? "0"+i : i;
}

// Ustalenie indeksu timera danego pliku
function timed_idx(jpk_id) {

	for(let i=0; i<timed.length; i++)
		if(timed[i].jpk_id == jpk_id)
			return timed[i].id;
}	

// Polling o status pliku podczas tworzenia
export function poll_status() {

	const jpk_ids= $.map(timed, function(n, i) { return n.jpk_id; });
	
	if(jpk_ids.length>0) {
	    $.ajax({
	    	dataType: "json",
	        url: "/jpk/"+jpk_ids+"/task/",
	        success: function(data) {
				$.each(data, function(jpk_id, value) {
					const index= timed_idx(jpk_id);
					const row= table.row(index);
					
	        		if(value.stan != 'W KOLEJCE' && value.stan != 'TWORZENIE') {
						timer_del(jpk_id);
						row.data().stan= value.stan;
						show_details(row);	        			
	        		}
	        		else {
	        			timer_add(index, jpk_id, value.czas);
	        			row.data().stan= value.stan+'<br/><span class="small">'+value.czas+'</span>';
	        		}
	        		row.invalidate();
				});
	        },
	        timeout: 2000
	    });
		setTimeout(poll_status, 3000);	    
	}
}
