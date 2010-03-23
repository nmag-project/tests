(* ********** Start of original pyfem3.ml ********** *)


open Pycaml;;

(* Specify a pill type: integer array *)

let array_pill_name = "ocaml array";;


let () = register_ocamlpill_types
    [| array_pill_name;
    |]
;;

let _sample_array_pill = [| 1 |];;


let (ocamlpill_from_array, array_from_ocamlpill) =
  make_ocamlpill_wrapper_unwrapper array_pill_name _sample_array_pill;;

(* End of specification of integer array pill type *)

(* Generic utilities for creating Python extension modules. Should be
   moved to Pycaml *)

let my_register_for_python mod_dict stuff =
  Array.iter
    (fun (python_name, value) ->
       ignore(pydict_setitemstring (mod_dict, python_name, value)))
    stuff;;

let my_register_pre_functions_for_python mod_dict stuff =
  Array.iter
    (fun (python_name, pre_fun) ->
       ignore(pydict_setitemstring (mod_dict, python_name, pre_fun python_name)))
    stuff;;

(* End of generic utilities *)

(* Wrappers for functionality provided in ML *)


let _py_square =
  python_pre_interfaced_function [|FloatType|]
    (fun py_args ->
       let ml_arg = pyfloat_asdouble py_args.(0) in
       let ml_result = Functionality.square ml_arg in
       let py_result = pyfloat_fromdouble ml_result
       in
         py_result)
;;

let _py_make_consecutive_integers = 
  python_pre_interfaced_function [| IntType |]
    (fun py_args ->
       let ml_arg = pyint_asint py_args.(0) in
       let ml_result = Functionality.make_consecutive_integers ml_arg in
       let py_result = ocamlpill_from_array ml_result
       in
         py_result)
;;

let _py_add_up =
  python_pre_interfaced_function [| CamlpillType |]
    (fun py_args ->
      let ml_arg = array_from_ocamlpill py_args.(0) in
      let ml_result = Functionality.add_up ml_arg in
      let py_result = pyint_fromint ml_result in
      py_result)
;;


let create_nsimcore_module () = 
  (*
  let _ =
    register_for_python
      [|("mesher_defaults",ocamlpill_from_mesher_defaults_int !opt_mesher_defaults);
	("mesher_default_gendriver",ocamlpill_from_mg_gendriver default_gendriver);
	("empty_element",_py_empty_element);
      |]
in
*)
  let _py_mod_ocaml = ourpy_initemptymodule "functionality" in
  let _py_mod_ocaml_dict = pymodule_getdict _py_mod_ocaml in
    my_register_pre_functions_for_python _py_mod_ocaml_dict
      [|("square", _py_square);
        ("make_consecutive_integers", _py_make_consecutive_integers);
        ("add_up", _py_add_up);|];;

let _ = Callback.register "create_nsimcore_module" create_nsimcore_module;;


