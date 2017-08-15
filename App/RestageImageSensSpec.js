/*
Progression table
        Progression | No Progression | Total
    +
    -
  Total
*/

class SensSpec{
	constructor(truePositives, falsePositives, trueNegatives, falseNegatives){
		this.truePositives = truePositives;
		this.trueNegatives = trueNegatives;
		this.falseNegatives = falseNegatives;
		this.falsePositives = falsePositives;
	};
    truePos(){
    	return this.truePositives;
    };
    trueNeg(){
    	return this.trueNegatives;
    };
    falsePos(){
    	return this.falsePositives;
    };
    falseNeg(){
    	return this.falseNegatives;
    };
    toMatrix(){
    	return [[this.truePositives, this.falsePositives, this.truePositives + this.falsePositives],
    			[this.falseNegatives, this.trueNegatives, this.trueNegatives + this.falseNegatives],
    			[this.truePositives + this.falseNegatives, this.falsePositives + this.trueNegatives, 
    				this.truePositives + this.falseNegatives + this.falsePositives + this.trueNegatives]];
    };
};

function filterData(data, source, Line, Regimen, Threshold){
  console.log('filtering data, inputs: ' + source + ', '+ Line + ', ' + Regimen +', ' + Threshold);
	var data = data,
		truePositives = 0,
		trueNegatives = 0,
		falsePositives = 0,
		falseNegatives = 0;

	if(Line){
		var Line = Line;
	} else {
		var Line = '';
	};
	if(Regimen){
		var Regimen = Regimen;
	} else {
		var Regimen = '';
	};
	if(Threshold){
		var Threshold = Threshold;
	} else {
		var Threshold = 0;
	};
	if(source.indexOf('exo') != -1){
		var dna = 2;
	} else if (source.indexOf('cf') != -1){
		var dna = 3;
	};
	for(var i = 0; i < data.length; i++){
		var temp = data[i].split(',');
		if(temp[4].indexOf(Line) != -1){
			if(temp[5].indexOf(Regimen) != -1){
				if( 'PD' == temp[1] & temp[dna] != '' ){
					if(temp[dna] > Threshold){
						truePositives += 1;
					} else {
						falseNegatives += 1;
					};
				} else if(temp[dna] != ''){
					if(temp[dna] > Threshold){
						trueNegatives += 1;
					} else {
						falsePositives += 1;
					};
				};
			};
		};
	};

	return new SensSpec(truePositives, falsePositives, trueNegatives, falseNegatives);
};

function addtoTable(tableID, matrix){
	var table = document.getElementById(tableID),
		trows = table.rows;
	for(var r = 1; r < trows.length; r++){
		var row = trows[r];
		for(var c = 0; c < 3; c++){
			var newCell = row.insertCell();
			newCell.appendChild(document.createTextNode(matrix[r-1][c]));
		}; 
	};
};

function changeTable(tableID, matrix){
	var table = document.getElementById(tableID),
		trows = table.rows;
	for(var r = 1; r < trows.length; r++){
		var row = trows[r];
		for(var c = 1; c < row.cells.length; c++){
			row.cells[c].innerHTML = matrix[r-1][c-1];
		}; 
	};
};

function newCriteria(){
	var line = document.getElementById('inputline').value,
		regimen = document.getElementById('inputregimen').value,
		threshold = +document.getElementById('inputthreshold').value;
	if(threshold == ''){
		threshold = 0;
	};
	return [line, regimen, threshold];
};

function statMeasurements(tableID, sensspec){
    document.getElementById(tableID+'sens').innerHTML = sensspec.truePos()/(sensspec.truePos() + sensspec.falseNeg());
    document.getElementById(tableID+'spec').innerHTML = sensspec.trueNeg()/(sensspec.trueNeg() + sensspec.falsePos());
    document.getElementById(tableID+'prec').innerHTML = sensspec.truePos()/(sensspec.truePos() + sensspec.falsePos());
    document.getElementById(tableID+'npv').innerHTML = sensspec.trueNeg()/(sensspec.trueNeg() + sensspec.falseNeg());
   
};

var recistData = String(\""& RestagingAnalysis::numRecist &"\").split(';');

var exoDNA = filterData(recistData, 'exoDNA', '', '', 0); 
var cfDNA = filterData(recistData, 'cfDNA', '', '', 0);
console.log(exoDNA);
console.log(cfDNA);
console.log(exoDNA.toMatrix());
console.log(cfDNA.toMatrix());
addtoTable('exo', exoDNA.toMatrix());
addtoTable('cf', cfDNA.toMatrix());
statMeasurements('exo', exoDNA);
statMeasurements('cf', cfDNA);


$('#go').click(function(){
    console.log('go clicked');
	var criteria = newCriteria();
	var exoDNA = filterData(recistData, 'exoDNA', criteria[0], criteria[1], criteria[2]);
	var cfDNA = filterData(recistData, 'cfDNA', criteria[0], criteria[1], criteria[2]);
    console.log(exoDNA);
    console.log(cfDNA);
	changeTable('exo', exoDNA.toMatrix());
	changeTable('cf', cfDNA.toMatrix());
});