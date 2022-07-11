# Pacha
*Created by Turtleisaac*

Dynamic region-agnostic Nintendo DS ROM patcher

Creates patches which are capable of replacing individual narc files or even narc subfiles without touching anything else in the ROM.

#Notes

* Arm9, arm7, and overlay patches are produced using xdelta3. Therefore, patches created using Pacha which contain modifications to the code binaries are locked to only working on the specific region original ROM used in creating the patch file.

# Future Plans

* Will eventually support "multi-patches" where a provided patch file contains required patches and optional ones for the end-user to choose from. This will enable hack developers to release a single patch for their hack and have the user select which of the sub-patches they would like to apply.
* Further refinement of the code binary patch generation system may eventually allow for developers to write python code which can dynamically apply ASM and other modifications to the code binaries on a per-file basis. Compatibility between developer-produced python code is not guaranteed.

