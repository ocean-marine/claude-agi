/**
 * 数値比較プログラム
 * 3.12と3.8のどちらが大きいかを比較する
 */

function compareNumbers(num1, num2) {
    console.log('=== 数値比較結果 ===');
    console.log(`数値1: ${num1}`);
    console.log(`数値2: ${num2}`);
    
    if (num1 > num2) {
        console.log(`結果: ${num1} > ${num2}`);
        console.log(`${num1}の方が大きいです`);
    } else if (num1 < num2) {
        console.log(`結果: ${num1} < ${num2}`);
        console.log(`${num2}の方が大きいです`);
    } else {
        console.log(`結果: ${num1} = ${num2}`);
        console.log(`両方の数値は等しいです`);
    }
    
    console.log('==================');
}

// 3.12と3.8を比較
const number1 = 3.12;
const number2 = 3.8;

compareNumbers(number1, number2);