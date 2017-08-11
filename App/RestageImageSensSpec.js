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
	}
    truePos(){
    	return this.truePositives;
    }
    trueNeg(){
    	return this.trueNegatives;
    }
    falsePos(){
    	return this.falsePositives;
    }
    falseNeg(){
    	return this.falseNegatives;
    }
    toMatrix(){
    	return [[this.truePositives, this.falsePositives, this.truePositives + this.falseNegatives],
    			[this.falseNegatives, this.trueNegatives, this.truePositives + this.falseNegatives],
    			[this.truePositives + this.falseNegatives, this.falsePositives + this.trueNegatives, 
    				this.truePositives + this.falseNegatives + this.truePositives + this.falseNegatives]];
    }
};

function filterData(data, source, Line, Regimen, Threshold){
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
	}''
	for(var i = 0; i < data.length; i++){
		var temp = data[i].split(',');
		if(temp[4].indexOf(Line) != -1){
			if(temp[5].indexOf(Regimen) != -1){
				if( 'PD' == temp[1] ){
					if(temp[dna] > Threshold){
						truePositives += 1;
					} else {
						falseNegatives += 1;
					};
				} else if(temp[DNA] <= Threshold){
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
			newCell.appendChild(createTextNode(matrix[r][c]));
		}; 
	};
};

function changeTable(tableID, matrix){
	var table = document.getElementById(tableID),
		trows = table.rows;
	for(var r = 1; r < trows.length; r++){
		var row = trows[r];
		for(var c = 1; c < row.cells.length; c++){
			row.cells[c].innerHTML = matrix[r][c-1];
		}; 
	};
};

function newCriteria(){
	var line = document.getElementById('inputline').innerHTML,
		regimen = document.getElementById('inputregimen').innerHTML,
		threshold = document.getElementById('inputthreshold').innerHTML;
	if(threshold == ''){
		threshold = 0;
	};
	return [line, regimen, threshold] 
};

recistData = String("").split(';');

var exoDNA = filterData(recistData, 'exoDNA', '', '', 0); 
var cfDNA = filterData(recistData, 'cfDNA', '', '', 0);

addtoTable('exo', exoDNA.toMatrix());
addtoTable('cf', cfDNA.toMatrix());

$('#go').click(function(){
	var [line, regimen, threshold] = newCriteria;
	exoDNA = filterData(recistData, 'exoDNA', line, regimen, threshold);
	cfDNA = filterData(recistData, 'cfDNA', line, regimen, threshold);
	changeTable('exo', exoDNA.toMatrix());
	changeTable('cf', cfDNA.toMatrix());
});