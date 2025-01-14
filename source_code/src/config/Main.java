package config;


import java.util.Random;

import config.Constants;
import config.PropParser;


/**
 * Designed to be run with a properties file specified
 * > java -jar Main filename.properties
 * 
 * This is just a toy program setup to show you how to freeze your code and run different experiments
 * once you have finished all the details.
 * 
 * @author Jason Yoder
 *
 */
public class Main {
	
	public static void main(String[] args) {
		// String filename = args[0];    // to avoid needing to change source code at all
		// To use this:
		// Right Click on Main.java->Run As->Run Configurations
		// Select Arguments->Variables->String Prompt(i.e. ${string_prompt}) -> Run
		// Then the program will ask you for the path to the configuration you want to use
		String filename = Constants.PATH_CONF_FILE;
		PropParser.load(filename);
	
		int runs = Constants.RUNS;
		for (int seed=0; seed<runs; seed++) {				
			//run code with seed
			Random r = new Random(seed);
			
			// you get better randomization if you double randomize from the original seed
			r = new Random( r.nextInt(10000) );
			
			//you can access the variables you want directly like so:
			if (r.nextDouble() < Constants.MUT_RATE) { //notice that this variable is set from the configuration file
				System.out.println("A mutation occurred on seed: "+ seed);
			}

		}
	}


}
