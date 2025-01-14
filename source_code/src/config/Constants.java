package config;


/**
 * This file should list exactly the strings to be referenced from the code
 * base. It will load the user specified values from a configuration file and
 * other files that are not meant to be user adjustable.
 * 
 * @author Jason Yoder
 *
 */
public class Constants {

	// Properties (user configurable)
	public static final int RUNS = Integer.parseInt(PropParser.getProperty(ConstantToPropertyMap.RUNS));
	public static final int POP_SIZE = Integer.parseInt(PropParser.getProperty(ConstantToPropertyMap.POP_SIZE));
	public static final int GENOME_LEN = Integer.parseInt(PropParser.getProperty(ConstantToPropertyMap.GENOME_LEN));
	public static final int GENERATIONS = Integer.parseInt(PropParser.getProperty(ConstantToPropertyMap.GENERATIONS));
	public static final double MUT_RATE = Double.parseDouble(PropParser.getProperty(ConstantToPropertyMap.MUT_RATE));
	public static final double RECOM_RATE = Double.parseDouble(PropParser.getProperty(ConstantToPropertyMap.RECOM_RATE));

	// Constants (not user configurable)
	public static final String PATH_CONF_FILE = "src/config/default.properties";
}
