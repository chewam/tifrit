(function(){
  var nav=document.getElementById('nav'),b=document.querySelector('.burger'),m=document.getElementById('menu');
  function onScroll(){nav.classList.toggle('solid',window.scrollY>40||!document.body.classList.contains('has-hero'))}
  onScroll();addEventListener('scroll',onScroll,{passive:true});
  if(b){b.addEventListener('click',function(){var o=m.classList.toggle('open');b.setAttribute('aria-expanded',o);nav.classList.toggle('menu-open',o)});}
  // apparition douce
  if('IntersectionObserver' in window){
    var els=document.querySelectorAll('main h2, main .card, main .gallery > *, main .fact, main .sejour, main .quote, main .note, main blockquote, main > .wrap > .ph');
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.08,rootMargin:'0px 0px -5% 0px'});
    els.forEach(function(el){el.classList.add('reveal');io.observe(el)});
  }
  var q=new URLSearchParams(location.search).get('sejour'),sel=document.getElementById('sejour');
  if(q&&sel){sel.value=q;}
  var cal=document.getElementById('cal');
  if(!cal)return;
  var dispo=JSON.parse(cal.getAttribute('data-dispo')||'{}'),lang=cal.getAttribute('data-lang')||'fr';
  var full=(dispo.complet||[]).map(function(r){return [new Date(r.du),new Date(r.au)]});
  var days={fr:['L','M','M','J','V','S','D'],en:['M','T','W','T','F','S','S'],de:['M','D','M','D','F','S','S']}[lang];
  var legend={fr:'Complet',en:'Fully booked',de:'Ausgebucht'}[lang];
  var today=new Date();today.setHours(0,0,0,0);
  var wrap=document.createElement('div');wrap.className='cal';
  for(var k=0;k<3;k++){
    var first=new Date(today.getFullYear(),today.getMonth()+k,1),y=first.getFullYear(),mo=first.getMonth();
    var t=document.createElement('table'),cap=document.createElement('caption');
    cap.textContent=first.toLocaleDateString(lang,{month:'long',year:'numeric'});t.appendChild(cap);
    var tr=document.createElement('tr');days.forEach(function(d){var th=document.createElement('th');th.textContent=d;tr.appendChild(th)});t.appendChild(tr);
    var start=(first.getDay()+6)%7,n=new Date(y,mo+1,0).getDate(),row=document.createElement('tr');
    for(var i=0;i<start;i++)row.appendChild(document.createElement('td'));
    for(var d=1;d<=n;d++){
      var dt=new Date(y,mo,d),td=document.createElement('td');td.textContent=d;
      if(dt<today)td.className='past';
      else if(full.some(function(r){return dt>=r[0]&&dt<=r[1]}))td.className='full';
      if(dt.getTime()===today.getTime())td.className+=' today';
      row.appendChild(td);
      if(row.children.length===7){t.appendChild(row);row=document.createElement('tr');}
    }
    if(row.children.length)t.appendChild(row);
    wrap.appendChild(t);
  }
  cal.appendChild(wrap);
  var lg=document.createElement('p');lg.className='legend';lg.innerHTML='<i></i>'+legend;cal.appendChild(lg);
})();
