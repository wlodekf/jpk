const path = require('path');
const webpack = require("webpack");
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');

module.exports = {

  mode: 'production',

  entry: {
  	jpk: './src/index.js',
  },
  
  plugins: [
    new CleanWebpackPlugin(['../../app/static/bundle/jpk/*']),

    new HtmlWebpackPlugin({
    	filename: '../../../../app/templates/app/body.html',
    	template: './src/body.html',
    	inject: false
    }),
  ],

  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, '../../app/static/bundle/jpk'),
    publicPath: 'bundle/jpk/',
  },
  
  module: {
     rules: [
       {
         test: /\.css$/,
         use: [
           'style-loader',
           'css-loader'
         ]
       },
	   {
	      test: /\.m?js$/,
	      exclude: /(node_modules|bower_components)/,
	      use: {
	        loader: 'babel-loader',
	        options: {
	          presets: ['@babel/preset-env']
	        }
	      }
	   }
  	]
  },
  
  optimization: {
    minimize: true,
//    runtimeChunk: 'single',
    
//    splitChunks: {
//      cacheGroups: {
//        vendor: {
//          test: /[\\/]node_modules[\\/]/,
//          name: 'vendors',
//          chunks: 'all'
//        }
//      }
//    }

  },
};

