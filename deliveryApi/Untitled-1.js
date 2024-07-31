// class add {
//     constructor(name, age) {
//         this.name = name;
//         this.age = age;
//         console.log(this);
//     }
// }

// const dc = new add(2,3)


// for(let i= 0; i < 5; i++){
//     setTimeout(() => {
//         console.log('adada', i)
//     },500)
// }

// function upper(strings, ...values){
//     var ret = "";
//     console.log("strings ", strings)
//     for(let i = 0; i< strings.length; i++){
//          if( i > 0 ){
//              ret += String(values[i-1]).toUpperCase()
//          }
//          ret += strings[i]
//     }
//     return ret
// }
// var tragedy = "tragedy" 
// var comedy = "comedy";
// console.log(upper`i thought my was a ${tragedy} but now i realize it was a ${comedy}`)

// var response =  [ 
//     {
//         name: undefined
//     },
//     {
//         name:'doe'
//     }
// ]

// var [
//     {
//         name: firstName = "jane"
//     },
//     ...lastName
// ] = response;

// console.log(firstName, lastName)

// let x = {}
// if(x){
//     console.log("x")
// }
// else{
//     console.log("falsy")
// }
console.log(this)
function a () {
    
    console.log(this.A)
    nested = () => {
        console.log(this.A)
    }
    nested()
}

a()