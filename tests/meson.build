decompiler_test = executable('decompiler_test',
  'main.cc',
  preparation_check,
  '../src/unittests/paramactive.cc',
  '../src/unittests/pcodeinject.cc',
  '../src/unittests/testsegmented.cc',
  '../src/unittests/testqualifiers.cc',
  '../src/decompiler/xml_arch.cc',
  '../src/decompiler/loadimage_xml.cc',
  include_directories: incs,
  dependencies: zlib,
  link_with: [ghidra_base_static, ghidra_decompiler_static, slgh_static, libdecomp_static])

x86_languages = processor_dir / 'x86' / 'data' / 'languages'
foreach spec : ['x86.ldefs', 'x86-16.pspec', 'x86-16-real.pspec', 'x86-16.cspec', 'x86.pspec', 'x86gcc.cspec', 'x86-64.pspec', 'x86-64-gcc.cspec']
  configure_file(input: x86_languages / spec, output: spec, copy: true)
endforeach
x86_test_sla = custom_target('x86-test-sla',
  input: x86_languages / 'x86.slaspec',
  output: 'x86.sla',
  command: [sleighc_exe, '@INPUT@', '@OUTPUT@'])
x86_64_test_sla = custom_target('x86-64-test-sla',
  input: x86_languages / 'x86-64.slaspec',
  output: 'x86-64.sla',
  command: [sleighc_exe, '@INPUT@', '@OUTPUT@'])

test('ghidra-native-unittests', decompiler_test,
  depends: [x86_test_sla, x86_64_test_sla],
  env: ['SLEIGHHOME=' + meson.current_build_dir()])

test('patch-preparation', python, args: files('test_apply_patches.py'),
  timeout: 90,
  depends: sleighc_exe,
  env: ['SLEIGHC=' + sleighc_exe.full_path()])
