$(function() {
  var blooddraws = [],
      therapies = [],
      progression = [],
      recist = [];

function parseDate(date, mdy) {
    var tempdate = date;
console.log(tempdate);
    if( tempdate == '' ){
      console.log('empty date');
      console.log(date);
      return 0;
    };
    if (tempdate != '') {
      tempdate = tempdate.split(' ');
      tempdate = tempdate[0].split('-');
    };
    if (tempdate[0].indexOf('/') != -1) {
      tempdate = tempdate[0].split('/');
    };
    if(mdy == true){var newDate = (Date.UTC(tempdate[2], tempdate[0] - 1, tempdate[1])); } else {
      var newDate = (Date.UTC(tempdate[0], tempdate[1] - 1, tempdate[2]));
    };
    return newDate;
  };


// // Outdated
// function followUps(blooddraws, therapies){
//     var i = 0,
//         j = 0,
//         k = 1,
//         r = 0,
//         bool = true,
//         b = 0,
//         thmoves = 0;

//     var bdkeys = Object.keys(blooddraws),
//         thkeys = Object.keys(therapies),
//         rskeys = Object.keys(recist);
//     while(bool){
//       if(b >= bdkeys.length){ bool = false }
//       else if(blooddraws[bdkeys[b]].drawDate <= therapies[thkeys[0]].start){
//           blooddraws[bdkeys[b]].line = 'Baseline';
//           b++;
//       } else { bool = false; };
//     };

//     while( i < bdkeys.length - 1 && j < thkeys.length && k < bdkeys.length){
//         if(k <= i){k = i + 1};
//         var bd = blooddraws[bdkeys[i]],
//             bd2 = blooddraws[bdkeys[k]],
//             rs = recist[rskeys[r]],
//             th = therapies[thkeys[j]];
        
//       console.log(bd);
//       console.log(bd2);
//       console.log(th);
//       console.log('thmoves: ' + thmoves);
//         if(bd['line']){
//             if(bd2['line'] == 'Baseline'){ i++; k++; continue; }; 
//                 console.log('bd has line');
//             if(bd2['drawDate'] < th['end']){
//                 console.log('bd before th end');
//                 console.log(thmoves);
//                 if(bd2['drawDate'] > th['start'] && thmoves == 0){
//                 console.log('pseudofollowup');
//                     bd2['pseudoFollowup'] = true;
//                     k++;
//                 } else if( bd2['drawDate'] <= th['start'] && thmoves == 1){
//                         console.log('checking if followup');
//                     if(therapies[thkeys[j-1]]['line'] != th['line']){
//                           console.log('followUp');
//                         bd2['followUp'] = true;
//                         if(bd2['line']){ } else {
//                             console.log('setting line A ' + therapies[thkeys[j-1]]['line']);
//                             bd2['line'] = therapies[thkeys[j-1]]['line'];
//                         };
//                         i = k;
//                         k++;
//                         thmoves = 0;
//                     } else {
//                         bd2['pseudoFollowup'] = true;
//                         k++;
//                         thmoves = 0;
//                     };
//                 } else if ( thmoves > 0 && th['line'] == therapies[thkeys[j-1]]['line']){
//                     console.log('testing');
//                     thmoves = 0;
//                 } else {
//                         console.log('should not be here'); 
//                     break;
//                 };
//             } else if (bd2['drawDate'] >= th['end']){
//                 console.log('bd after th end');
//                 if(j + 1 == thkeys['length'] && thmoves == 0){
//                     bd2['followUp'] = true;
//                     bd2['line'] = th['line'];
//                     j++;
//                 } else {
//                     if(therapies[thkeys[j+1]]){
//                       if(bd2['drawDate'] <= therapies[thkeys[j+1]]['start']){
//                           console.log('setting line B: ' + th['line']);
//                           bd2['line'] = th['line'];
//                       };
//                     };
//                     if(thmoves == 0) {
//                         j++;
//                         thmoves++;
//                     } else {
//   console.log('bd2 is __line');
//                         i = k;
//                         k++;
//   j++;
//                         thmoves = 0;
//                     };
//                 };
//             };
//         } else {
//             if(bd['drawDate'] > th['start']){
//                 if(bd['drawDate'] < th['end']){
//                     i++;
//                 } else {
//                     j++;
//                     thmoves++;
//                 };
//             } else if (bd['drawDate'] <= th['start']){
//                     if(thmoves >= 1){
//                         console.log('setting log C');
//                         bd['line'] = therapies[thkeys[j-1]]['line'];
//                         thmoves = 0;
//                     } else {
//                         i++;
//                     };
//             };
//         };
//     };

// };

// function createDateRanges(therapies, recist){
//     var thkeys = Object.keys(therapies),
//         rskeys = Object.keys(recist),
//         r = 0,
//         regimen = 0,
//         pline = '',
//         bool = false,
//         firstCT = recist[rskeys[0]],
//         ranges = [];

//     if (rskeys.length < 2) {
//         console.log('not enough CT scans');
//       return
//     };
//     for(var i = 0; i < thkeys.length; i++){
//         var th = therapies[thkeys[i]],
//             s = 0;

//         if(pline != th.line || pline == ''){
//             pline = th.line;
//             regimen += 1;
//         };
//         while(bool == false && r < rskeys.length){
//             var rsImage = recist[rskeys[r]];
//             if(rsImage['imageDate'] < th['start']){
//                 r += 1;
//             } else {
//                 if(rsImage['imageDate'] <= th['end']){
//                     s += 1;
//                     r += 1;
//                     ranges.push({
//                         R: regimen,
//                         S: s,
//                         start: th['start'],
//                         end: rsImage['imageDate']
//                     });
//                 } else {
//                     if(thkeys[i+1]){
//                         if(therapies[thkeys[i+1]]['end'] <= rsImage['imageDate']){
//                             bool = true;
//                         } else if(therapies[thkeys[i+1]]['start'] >= rsImage['imageDate']) {
//                             s += 1;
//                             r += 1;
//                             ranges.push({
//                                 R: regimen,
//                                 S: s,
//                                 start: th['start'],
//                                 end: rsImage['imageDate']
//                             });
//                             bool = true;
//                         } else if(Math.abs(therapies[thkeys[i+1]]['start'] - rsImage['imageDate']) < 604800000 && s == 0){
//                             s += 1;
//                             ranges.push({
//                                 R: regimen,
//                                 S: s,
//                                 start: th['start'],
//                                 end: rsImage['imageDate']
//                             });
//                             bool = true;
//                         } else { bool = true};
//                     } else {
//                         s += 1;
//                         ranges.push({
//                             R: regimen,
//                             S: s,
//                             start: th['start'],
//                             end: rsImage['imageDate']
//                         });
//                         bool = true;
//                     };
//                 };
//             };
//         };
//         bool = false;
//     };
//     return ranges;
// };

// function assignRS(ranges, blooddraws){
//     var ranges = ranges,
//         blooddraws = blooddraws,
//         looper = 0,
//         bdkeys = Object.keys(blooddraws);

//     for(var i = 0; i < bdkeys.length; i++){
//         var bddd = blooddraws[bdkeys[i]]['drawDate'];
//         for(var j = 0; j < ranges.length; j++){
//             var range = ranges[j];
//             if(bddd >= range.start && bddd <= range.end){
//                 if(blooddraws[bdkeys[i]]['R']){
//                     blooddraws[bdkeys[i]]['R'].push(range.R);
//                     blooddraws[bdkeys[i]]['S'].push(range.S);
//                 } else {
//                     blooddraws[bdkeys[i]]['R'] = [range.R];
//                     blooddraws[bdkeys[i]]['S'] = [range.S];          
//                 };
//             }
//         }; 
//     };
//     return blooddraws;
// };

  var therapylist = String("& GraphAnalysis::TherapyList &").split(';');
console.log('therapy list');
console.log(therapylist);
  var tseries = [];
  for (var i = 0; i < therapylist.length; i++) {
    var temp = therapylist[i].split(',');
    if(temp[2]==''){
      if(i +  1 < therapylist.length){
        var temp2 = therapylist[i + 1].split(',');
        temp[2] = parseDate(temp2[1]);
      } else {
        temp[2] = new Date().getTime()
      };
    } else {temp[2] = parseDate(temp[2])};
    var point = {
      x: 0,
      therapyType: temp[0],
      low: parseDate(temp[1]),
      high: temp[2],
      regimen: temp[3],
      line: temp[4],
    };
    tseries.push(point);
    therapies.push({
      start: parseDate(temp[1]),
      end: temp[2],
      regimen: temp[3],
      line: temp[4],
    });
  };
  var lbxtemp = String("& GraphAnalysis::LiqBiopsyList &").split(';');
  var ddpcr = String("& GraphAnalysis::ddPCRDataTL &").split(';');
console.log('lbx temp');
console.log(lbxtemp);
console.log('ddpcr');
console.log(ddpcr);
  for(var i = 0; i<ddpcr.length; i++){
    ddpcr[i] = ddpcr[i].split(',');
  };
console.log(ddpcr);
  var lbx = [];
  for (var i = 0; i < lbxtemp.length; i++) {
    var color = '#e4e2dc';
    var date = parseDate(lbxtemp[i]);
    blooddraws.push({ drawDate: date});
    var point = {
      x: 0,
      y: date,
    };
    for(var j = 0; j<ddpcr.length; j++){
      if(date == parseDate(ddpcr[j][0])){
        if(ddpcr[j][2] == 'exoDNA'){
          if(color == '#e4e2dc'){ 
            color = '#18e707';
            point['surge'] = 'exoDNA';
            blooddraws[i]['surge'] = 'exoDNA';
            point['exoDNA'] = ddpcr[j][1];
          } else { 
            color = '#4ee4d3';
            point['surge'] = 'both';
            blooddraws[i]['surge'] = 'both';
            point['exoDNA'] = ddpcr[j][1];
          };
        } else if(ddpcr[j][2] == 'cfDNA'){
          if(color == '#e4e2dc'){
            color = 'Blue';
            point['surge'] = 'cfDNA';
            blooddraws[i]['surge'] = 'cfDNA';
            point['cfDNA'] = ddpcr[j][1];
          } else { 
            color = '#4ee4d3';
            point['surge'] = 'both';
            blooddraws[i]['surge'] = 'both';
            point['cfDNA'] = ddpcr[j][1];
          };
        };
      };
    };
    point.color = color;
    lbx.push(point);  
  };
console.log('lbx');
console.log(lbx);
var il = String("& GraphAnalysis::ImagingList &").split(';');
console.log('image list');
console.log(il);
  for( var i = 0; i< il.length; i++){
    var tempImage = il[i].split(','),
        date = parseDate(tempImage[0]),
        event = tempImage[1];
      recist.push({ 'imageDate': date,
                    'event': event});
  };
console.log('recist');
console.log(recist);
  for(var i = 0; i < Object.keys(recist).length; i++){
    var image = recist[Object.keys(recist)[i]];
    var point = {
       x: 1,
       y: image['imageDate'],
       event: image['event']
    };
    recistG.push(point);
  };
  var series = [{
      name: 'Therapy',
      data: tseries,
    }, {
      type: 'scatter',
      name: 'Liquid Biopsy',
      data: lbx,
    }, {
      type: 'scatter',
      name: 'Restaging Imaging',
      data: recistG,
    },];

Highcharts.chart('graph', {
    chart: {
        type: 'columnrange',
        inverted: true,
        zoomType: 'y',
    },
    xAxis: {
      categories: ['Therapy', 'Restaging Imaging'],
      title: {text: null},
    },
    title: {text: null},

    yAxis: {
      type: 'datetime',
      title: {text: null},
      legend: {
        enabled: false
      },
      followPointer: false,
      hideDelay: 100,
      shared: false,
  		},

    plotOptions: {
      series: {
        stickyTracking: false,
      },
    },
    tooltip: {
      formatter: function (){
          if(this.point.therapyType){
            if(this.point.line != ''){
              return '<h3><b>' + this.point.therapyType + '</b></h3><br><b>' + this.point.line + '</b><br><b>' +this.point.regimen + '</b><br>Start Date: ' + Highcharts.dateFormat('%m/%d/%y', this.y) + '<br>End Date: ' + Highcharts.dateFormat('%m/%d/%y', this.point.high);
            } else { return '<h3><b>' + this.point.therapyType + '</b></h3><br><b>' + this.point.regimen + '</b><br>Start Date: ' + Highcharts.dateFormat('%m/%d/%y', this.y) + '<br>End Date: ' + Highcharts.dateFormat('%m/%d/%y', this.point.high);
            }
          } else if(this.point.surge){
            if(this.point.surge == 'both'){
              return '<h3><b>' + this.series.name + '</b></h3><br>' + 'Date: ' + Highcharts.dateFormat('%m/%d/%y', this.y) + '<br>exoDNA: ' + this.point.exoDNA + '<br>cfDNA: ' + this.point.cfDNA;
            } else if(this.point.surge == 'exoDNA'){
              return '<h3><b>' + this.series.name + '</b></h3><br>' + 'Date: ' + Highcharts.dateFormat('%m/%d/%y', this.y) + '<br>exoDNA: ' + this.point.exoDNA;
            } else if(this.point.surge == 'cfDNA'){
return '<h3><b>' + this.series.name + '</b></h3><br>' + 'Date: ' + Highcharts.dateFormat('%m/%d/%y', this.y) + '<br>cfDNA: ' + this.point.cfDNA;
            };
          } else {
            return '<h3><b>' + this.series.name + '</b></h3><br>' + 'Date: ' + Highcharts.dateFormat('%m/%d/%y', this.y);
          };
      },
    },
    legend: {
        enabled: false
    },
    series: series,

});
console.log('blood draws');
console.log(blooddraws);
console.log('therapies');
console.log(therapies);
console.log('progression');
console.log(progression);

var ranges = createDateRanges(therapies, recist);

console.log('ranges');
console.log(ranges);
var bdRS = assignRS(ranges, blooddraws);
console.log('blooddraws with RS');
console.log(bdRS);

// $('#abd').click(function(){
//    var Lines = '';
//    for(var i = 0; i < Object.keys(blooddraws).length; i++){
//      Lines = Lines + blooddraws[Object.keys(blooddraws)[i]].line + '-';
//    };
//    theURL = \"fmp://$/" & Get ( FileName ) & "\?script=AssignBloodDrawLine&param=\" + Lines;
//    window.location = theURL ;
// });
//    var fulist = fus[0] + '-' + fus[1];
//    theURL = \"fmp://$/" & Get ( FileName ) & "\?script=WVSetFollowUps&param=\" + fulist;
//    window.location = theURL ;

// });