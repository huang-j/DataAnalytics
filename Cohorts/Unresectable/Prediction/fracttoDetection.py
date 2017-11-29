import pandas as pd
import numpy as np
import argparse


def process(csv, output):
	print('Reading CSV')
	df = pd.read_csv(csv, sep=',')

	print('Processing data')
	df = df.dropna(axis=0, how='any')
	df['prog'] = df['Recist'].apply(lambda x: 1 if x == 'PD' else 0)
	df['detectexo'] = df['exofract']
	df['detectcf'] = df['cffract']

	## set up detection for exoDNA
	df['detectexo'] = np.where( (df['prog'] == 1) & (df['detectexo'] > 0), 1, df['detectexo'])
	df['detectexo'] = np.where( (df['prog'] == 1) & (df['detectexo'] == 0), 0, df['detectexo'])
	df['detectexo'] = np.where( (df['prog'] != 1) & (df['detectexo'] == 1), 2, df['detectexo'])
	df['detectexo'] = np.where( (df['prog'] != 1) & (df['detectexo'] < 1), 1, df['detectexo'])
	df['detectexo'].loc[df['detectexo'] == 2] = 0
	## cfDNA
	df['detectcf'] = np.where( (df['prog'] == 1) & (df['detectcf'] > 0), 1, df['detectcf'])
	df['detectcf'] = np.where( (df['prog'] == 1) & (df['detectcf'] == 0), 0, df['detectcf'])
	df['detectcf'] = np.where( (df['prog'] != 1) & (df['detectcf'] ==1), 2, df['detectcf'])
	df['detectcf'] = np.where( (df['prog'] != 1) & (df['detectcf'] < 1), 1, df['detectcf'])
	df['detectcf'].loc[df['detectcf'] == 2] = 0

	df['exo'] = df['exofract'].apply(lambda x: 1 if x > 0 else 0);
	df['cf'] = df['cffract'].apply(lambda x: 1 if x > 0 else 0);
	# df['exoorcf'] = np.where( (df['exo'] == 1) | (df['cf'] == 1), 1, 0)
	# df['exoandcf'] = np.where( (df['exo'] == 1) & (df['cf'] == 1), 1, 0)
	df['exoorcf'] = np.where( ((df['detectexo'] + df['detectcf'] >= 1)), 1, 0)
	df['exoandcf'] = np.where( ((df['detectexo'] + df['detectcf'] == 2)), 1, 0)

	df['falsep'] = np.where( (df['prog'] == 0) & ((df['detectexo'] == 1) | (df['detectcf'] == 1)), True, False)
	df['falsen'] = np.where( (df['prog'] == 1) & ((df['detectexo'] == 0) | (df['detectcf'] == 0)), True, False)
	## to csv
	print('writing to output')
	df.to_csv(output, sep=',')

	## Condense

	## contingency tables
	print('Generating Contingency Tables')
	prog = df.loc[df['prog'] == 1];
	prog.to_csv('test1.csv')
	noprog = df.loc[df['prog'] == 0];
	noprog.to_csv('test2.csv')
	numProg = len(prog.index);
	print('Number of Progressers: ' + str(numProg))
	numNoProg = len(noprog.index);
	print('Number of Non-Progressers: ' + str(numNoProg))
	tpexo = prog['detectexo'].sum();
	tpcf = prog['detectcf'].sum();
	fpexo = noprog['detectexo'].sum();
	fpcf = noprog['detectcf'].sum();

	print('EXODNA')
	print('==================================')
	print('      Progression   No Progression')
	print('----------------------------------')
	print('  +    '+str(tpexo)+'          '+str(fpexo)+'         ')
	print('  -    '+str(numProg - tpexo)+'          '+str(numNoProg - fpexo)+'         ')
	print('---------------------------------- \n\n')

	print('CFDNA')
	print('==================================')
	print('      Progression   No Progression')
	print('----------------------------------')
	print('  +    '+str(tpcf)+'          '+str(fpcf)+'         ')
	print('  -    '+str(numProg - tpcf)+'          '+str(numNoProg - fpcf)+'         ')
	print('----------------------------------')

	print('\n\n\n**********************************\n\n\n')
	print('EXODNA')
	print('==================================')
	print('      Progression   No Progression')
	print('----------------------------------')
	print('  +    '+str(prog['exo'].sum())+'          '+str(numNoProg - noprog['exo'].sum())+'         ')
	print('  -    '+str(numProg - prog['exo'].sum())+'          '+str(noprog['exo'].sum())+'         ')
	print('---------------------------------- \n\n')

	print('CFDNA')
	print('==================================')
	print('      Progression   No Progression')
	print('----------------------------------')
	print('  +    '+str(prog['cf'].sum())+'          '+str(numNoProg - noprog['cf'].sum())+'         ')
	print('  -    '+str(numProg - prog['cf'].sum())+'          '+str(noprog['cf'].sum())+'         ')
	print('----------------------------------')
	

	print('\n\n\n**********************************\n\n\n')
	

	print('EXODNA OR CFDNA')
	print('==================================')
	print('      Progression   No Progression')
	print('----------------------------------')

	# print('  +    '+str(prog['exoorcf'].sum())+'          '+str(numNoProg - noprog['exoorcf'].sum())+'         ')
	# print('  -    '+str(numProg - prog['exoorcf'].sum())+'          '+str(noprog['exoorcf'].sum())+'         ')
	print('  +    '+str(prog['exoorcf'].sum())+'          '+str(noprog['exoorcf'].sum())+'         ')
	print('  -    '+str(numProg - prog['exoorcf'].sum())+'          '+str(numNoProg - noprog['exoorcf'].sum())+'         ')
	
	print('---------------------------------- \n\n')

	print('EXODNA AND CFDNA')
	print('**********************************')
	print('      Progression   No Progression')
	print('----------------------------------')
	# print('  +    '+str(prog['exoandcf'].sum())+'          '+str(numNoProg - noprog['exoandcf'].sum())+'         ')
	# print('  -    '+str(numProg - prog['exoandcf'].sum())+'          '+str(noprog['exoandcf'].sum())+'         ')
	print('  +    '+str(prog['exoandcf'].sum())+'          '+str(noprog['exoandcf'].sum())+'         ')
	print('  -    '+str(numProg - prog['exoandcf'].sum())+'          '+str(numNoProg - noprog['exoandcf'].sum())+'         ')
	print('----------------------------------')

	prog.to_csv('testprog.csv')
	noprog.to_csv('testnoprog.csv')
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Process CT prediction file')
	parser.add_argument('-c', '--csv', nargs=1, required=True, help='csv file', type=str)
	parser.add_argument('-o', '--output', nargs=1, required=True, help='csv file output', type=str)
	args = parser.parse_args()

	process(args.csv[0], args.output[0])