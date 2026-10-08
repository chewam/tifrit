(function(){
  var nav=document.getElementById('nav'),b=document.querySelector('.burger'),m=document.getElementById('menu');
  function onScroll(){nav.classList.toggle('solid',window.scrollY>40||!document.body.classList.contains('has-hero'))}
  onScroll();addEventListener('scroll',onScroll,{passive:true});
  if(b){b.addEventListener('click',function(){var o=m.classList.toggle('open');b.setAttribute('aria-expanded',o);nav.classList.toggle('menu-open',o)});}
  // apparition douce
  if('IntersectionObserver' in window){
    var els=document.querySelectorAll('main h2, main .card, main .gallery > *, main .fact, main .sejour, main .quote, main .note, main blockquote, main > .wrap > .ph, .confort > .wrap > div, .phare-panel, .split, .compare > a');
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.08,rootMargin:'0px 0px -5% 0px'});
    els.forEach(function(el){el.classList.add('reveal');io.observe(el)});
  }

  // formulaire de réservation : récapitulatif en direct, envoi par WhatsApp ou e-mail, déjà rédigé
  var form=document.querySelector('form.form');
  if(form){
    var ui={};try{ui=JSON.parse(form.getAttribute('data-ui')||'{}')}catch(e){}
    var lang=form.getAttribute('data-lang')||'fr';
    var q=new URLSearchParams(location.search).get('sejour');
    if(q){var r=form.querySelector('input[name=sejour][value="'+q+'"]');if(r)r.checked=true;}
    form.querySelectorAll('.stepper').forEach(function(st){
      var inp=st.querySelector('input'),out=st.querySelector('output');
      st.querySelectorAll('button').forEach(function(bt){bt.addEventListener('click',function(){
        var v=parseInt(inp.value,10)+parseInt(bt.getAttribute('data-step'),10);
        v=Math.max(parseInt(inp.getAttribute('data-min'),10),Math.min(parseInt(inp.getAttribute('data-max'),10),v));
        inp.value=v;out.value=v;update();
      })});
    });
    function fmt(d){if(!d)return '';var p=d.split('-');return p.length===3?p[2]+'/'+p[1]+'/'+p[0]:d}
    function val(n){var el=form.querySelector('[name='+n+']');return el?el.value:''}
    function state(){
      var sel=form.querySelector('input[name=sejour]:checked');
      var a=parseInt(val('adultes'),10)||0,k=parseInt(val('enfants'),10)||0;
      var people=a+' '+(a>1?ui.adultes:ui.adulte)+(k?', '+k+' '+(k>1?ui.enfants:ui.enfant):'');
      var ar=val('arrivee'),de=val('depart');
      var dates=ar&&de?(ui.recap_du||'{a} – {b}').replace('{a}',fmt(ar)).replace('{b}',fmt(de)):(ui.recap_a_preciser||'');
      var nav=form.querySelector('input[name=navette]').checked?ui.recap_oui:ui.recap_non;
      var nom=val('nom')||ui.preview_nom||'';
      return {sejour:sel?sel.getAttribute('data-titre'):'',prix:sel?sel.getAttribute('data-prix'):'',detail:sel?sel.getAttribute('data-detail'):'',personnes:people,dates:dates,navette:nav,nom:nom};
    }
    function message(){
      var s=state();
      var txt=(ui.preview_text||'').replace('{sejour}',s.sejour).replace('{dates}',s.dates).replace('{personnes}',s.personnes).replace('{navette}',s.navette).replace('{nom}',s.nom);
      var extra=[];var tel=val('tel'),mail=val('email'),msg=val('message');
      if(tel)extra.push(tel);if(mail)extra.push(mail);if(msg)extra.push(msg);
      return extra.length?txt+'\n'+extra.join('\n'):txt;
    }
    function update(){
      var s=state();
      ['sejour','dates','personnes','navette','prix','detail'].forEach(function(k){var el=document.querySelector('[data-recap='+k+']');if(el)el.textContent=s[k]});
      var pv=document.querySelector('[data-preview]');if(pv)pv.textContent=message();
    }
    form.addEventListener('input',update);form.addEventListener('change',update);update();
    var wa=form.getAttribute('data-wa'),mail=form.getAttribute('data-mail'),subject=form.getAttribute('data-subject')||'';
    function byMail(){location.href='mailto:'+mail+'?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(message())}
    var mb=form.querySelector('[data-mail]');if(mb)mb.addEventListener('click',function(){if(form.reportValidity())byMail()});
    if(!form.getAttribute('action')){
      form.addEventListener('submit',function(ev){
        ev.preventDefault();
        var w=window.open('https://wa.me/'+wa+'?text='+encodeURIComponent(message()),'_blank');
        if(!w)byMail();
      });
    }
  }

  // calendrier des disponibilités
  var cal=document.getElementById('cal');
  if(!cal)return;
  var dispo=JSON.parse(cal.getAttribute('data-dispo')||'{}'),clang=cal.getAttribute('data-lang')||'fr';
  var full=(dispo.complet||[]).map(function(r){return [new Date(r.du),new Date(r.au)]});
  var days={fr:['L','M','M','J','V','S','D'],en:['M','T','W','T','F','S','S'],de:['M','D','M','D','F','S','S']}[clang];
  var legend={fr:'Complet',en:'Fully booked',de:'Ausgebucht'}[clang];
  var today=new Date();today.setHours(0,0,0,0);
  var wrap=document.createElement('div');wrap.className='cal';
  for(var k=0;k<3;k++){
    var first=new Date(today.getFullYear(),today.getMonth()+k,1),y=first.getFullYear(),mo=first.getMonth();
    var t=document.createElement('table'),cap=document.createElement('caption');
    cap.textContent=first.toLocaleDateString(clang,{month:'long',year:'numeric'});t.appendChild(cap);
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
