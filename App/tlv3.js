$(function() {
  var blooddraws = [],
      therapies = [],
      progression = [],
      recist = []
      recistG = [];
  function add(a, b){
    return a + b;
  };
  function parseDate(date, mdy) {
      var tempdate = date;
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

  function combineLines(therapies){
    var temptherapies = [],
        index = 0,
        i2 = 1;
    temptherapies.push(therapies[index]);
    while(i2 < therapies.length){
      var line = temptherapies[index]['line'];
      while(i2 < therapies.length){
        if(therapies[i2]['line'] == line){
          temptherapies[index]['end'] = therapies[i2]['end'];
        } else {
          temptherapies.push(therapies[i2]);
          break
        };
        i2 += 1;
      };
      index += 1;
    };
    return temptherapies;
  };

  function recistPredict(recist, therapies, blooddraws, weeks){
    var tindex = 0,
        bdindex = 0,
        rsindex = 0,
        weeks = weeks * 604800000,
        lines = [],
        regimens = [],
        ep = [],
        cp = [];
    while(rsindex < recist.length){
      if(therapies[tindex + 1]) {
        if(recist[rsindex]['imageDate'] >= therapies[tindex + 1].start){
          tindex += 1;
        };
      };
      if(recist[rsindex]['imageDate'] < therapies[tindex].start){
        rsindex += 1;
      } else {
          var exopredict = [],
              cfpredict = [];
          for(var bd = bdindex; bd < blooddraws.length; bd++){
            if(blooddraws[bd]['drawDate'] >= recist[rsindex]['imageDate']){
              break
            } else if(blooddraws[bd]['drawDate'] <= recist[rsindex]['imageDate'] - weeks || blooddraws[bd]['drawDate'] < therapies[tindex].start){
              bdindex += 1;
            } else {
              if(recist[rsindex]['event'] == 'PD'){
                if(blooddraws[bd]['pos']){
                  if(blooddraws[bd]['pos'] == 'both'){
                    exopredict.push(1);
                    cfpredict.push(1);
                  } else if(blooddraws[bd]['pos'] == 'exoDNA'){
                    exopredict.push(1);
                    cfpredict.push(0);
                  } else if(blooddraws[bd]['pos'] =='cfDNA'){
                    exopredict.push(0);
                    cfpredict.push(1);
                  };
                } else {
                  exopredict.push(0);
                  cfpredict.push(0);
                };
              } else {
                if(blooddraws[bd]['pos']){
                  if(blooddraws[bd]['pos'] == 'both'){
                    exopredict.push(0);
                    cfpredict.push(0);
                  } else if(blooddraws[bd]['pos'] == 'exoDNA'){
                    exopredict.push(0);
                    cfpredict.push(1);
                  } else if(blooddraws[bd]['pos'] =='cfDNA'){
                    exopredict.push(1);
                    cfpredict.push(0);
                  };
                } else {
                  exopredict.push(1);
                  cfpredict.push(1);
                };
              };
              lines.push(blooddraws[bd]['line']);
              if(blooddraws[bd]['regimen'].indexOf('Fol') != 0){
                regimens.push('5-FU');
              } else if(blooddraws[bd]['regimen'].indexOf('Gem') != 0){
                regimens.push('GEM');
              } else {
                regimens.push(blooddraws[bd]['regimen'])
              };
            };
          };
          if(exopredict != []){
            var exofract = exopredict.reduce(add, 0)/exopredict.length;
          } else {
            console.log('no blooddraws before restaging');
            var exofract = 'N/A'
          };
          if(exopredict != []){
            var cffract = cfpredict.reduce(add, 0)/cfpredict.length;
          } else {
            console.log('no blooddraws before restaging');
            var cffract = 'N/A'
          };
          recist[rsindex]['exoPrediction'] = exofract;
          ep.push(exofract);
          recist[rsindex]['cfPrediction'] = cffract;
          cp.push(cffract);
          rsindex += 1;
      };
    };
    return [ep, cp, lines, regimens];
  };

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
            point['pos'] = 'exoDNA';
            blooddraws[i]['pos'] = 'exoDNA';
            point['exoDNA'] = ddpcr[j][1];
          } else { 
            color = '#4ee4d3';
            point['pos'] = 'both';
            blooddraws[i]['pos'] = 'both';
            point['exoDNA'] = ddpcr[j][1];
          };
        } else if(ddpcr[j][2] == 'cfDNA'){
          if(color == '#e4e2dc'){
            color = 'Blue';
            point['pos'] = 'cfDNA';
            blooddraws[i]['pos'] = 'cfDNA';
            point['cfDNA'] = ddpcr[j][1];
          } else { 
            color = '#4ee4d3';
            point['pos'] = 'both';
            blooddraws[i]['pos'] = 'both';
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
    var image = recist[i];
    var point = {
       x: 1,
       y: image['imageDate'],
       event: image['event'],
    };
    if(point.event == 'PD'){
      point.color = 'Red';
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
          } else if(this.point.pos){
            if(this.point.pos == 'both'){
              return '<h3><b>' + this.series.name + '</b></h3><br>' + 'Date: ' + Highcharts.dateFormat('%m/%d/%y', this.y) + '<br>exoDNA: ' + this.point.exoDNA + '<br>cfDNA: ' + this.point.cfDNA;
            } else if(this.point.pos == 'exoDNA'){
              return '<h3><b>' + this.series.name + '</b></h3><br>' + 'Date: ' + Highcharts.dateFormat('%m/%d/%y', this.y) + '<br>exoDNA: ' + this.point.exoDNA;
            } else if(this.point.pos == 'cfDNA'){
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

});