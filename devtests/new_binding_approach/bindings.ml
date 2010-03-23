(* open Pymlbindings *)
open Pycaml


(**************** shared **********************************************)
module type CONVERTER = sig
  type caml_type
  val pycaml_pyobject_type : pyobject_type
  val from_py : pyobject -> caml_type
  val to_py   : caml_type -> pyobject
end

module Converter_int = struct
  type caml_type = int
  let pycaml_pyobject_type = IntType
  let from_py = pyint_asint
  let to_py = pyint_fromint
end

module Converter_float = struct
  type caml_type = float
  let pycaml_pyobject_type = FloatType
  let from_py = pyfloat_asdouble
  let to_py = pyfloat_fromdouble
end

module Converter_list(Elt:CONVERTER) = struct
  type caml_type = Elt.caml_type array
  let pycaml_pyobject_type = ListType
  let from_py pylist = Array.map Elt.from_py (pylist_toarray pylist)
  let to_py camllist = pylist_fromarray (Array.map Elt.to_py camllist)
end

module Convertable_fun1 (ARG1: CONVERTER) (RES: CONVERTER) = struct
  type caml_type = ARG1.caml_type -> RES.caml_type
  let pycaml_pyobject_type = CallableType
  let from_py pyfunc = failwith "Not implemented yet."
  let to_py camlfun = 
    python_interfaced_function [| ARG1.pycaml_pyobject_type |]
      (fun pyargs -> RES.to_py (camlfun (ARG1.from_py pyargs.(0))))
end
(**********************************************************************)

(* ********** Start of original pyfem3.ml ********** *)


(* open Pycaml;; *)

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

(* This is being replaced by our more automatic wrapping utilities
let _py_square =
  python_pre_interfaced_function [|FloatType|]
    (fun py_args ->
       let ml_arg = pyfloat_asdouble py_args.(0) in
       let ml_result = Functionality.square ml_arg in
       let py_result = pyfloat_fromdouble ml_result
       in
         py_result)
;;
*)

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

module FF = Convertable_fun1 (Converter_float) (Converter_float)
module IL = Converter_list(Converter_int)
module IL_IL = Convertable_fun1
  (IL)
  (Converter_list(Converter_int))

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
    my_register_for_python _py_mod_ocaml_dict
      [|("square", FF.to_py Functionality.square);
	("reverse", IL_IL.to_py Functionality.reverse);
       (* ("make_consecutive_integers", _py_make_consecutive_integers);
        ("add_up", _py_add_up);*)|];;

let _ = Callback.register "create_nsimcore_module" create_nsimcore_module;;


