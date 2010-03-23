
let square x = x*.x;;

let make_consecutive_integers n = Array.init n (fun i -> i);;

let add_up array = Array.fold_left (+) 0 array;;

let reverse array = Array.of_list (List.rev (Array.to_list array)) ;;
